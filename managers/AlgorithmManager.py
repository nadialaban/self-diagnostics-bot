from helpers import log
from sqlalchemy.exc import SQLAlchemyError
from managers.Manager import Manager
from models import Algorithm, Question, Result


class AlgorithmManager(Manager):
    def __init__(self, *args):
        super(AlgorithmManager, self).__init__(*args)

    # Получение алгоритма
    def get(self, algorithm_id):
        algorithm = self.db.session.query(Algorithm).filter_by(id=algorithm_id).first_or_404()

        return algorithm.as_dict()

    # Получение доступных клинике алгоритмов
    def get_algorithms(self, clinic_id):
        algorithms = self.db.session.query(Algorithm).filter(Algorithm.creator.in_([-1, clinic_id])).all()
        algorithms = [alg.as_short_dict() for alg in algorithms]

        return algorithms

    # Получение доступных пациенту алгоритмов
    def get_enabled_algorithms(self, contract):
        algorithms = self.db.session.query(Algorithm).filter(Algorithm.id.in_(contract.algorithms)).all()
        algorithms = [alg.as_short_dict() for alg in algorithms]
        print(algorithms)
        return algorithms

    def is_depended_algorithm(self, algorithm_id):
        algorithms = self.db.session.query(Algorithm).filter(Algorithm.depended_algorithms.any(algorithm_id)).count()
        return algorithms

    # Удаление алгоритма.
    def remove(self, algorithm_id):
        try:
            self.db.session.query(Algorithm).filter_by(id=algorithm_id).delete()
            self.__commit__()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            log(e)
            return None
        return algorithm_id

    # Удаление вопросов.
    def remove_questions(self, algorithm_id):
        try:
            self.db.session.query(Question).filter_by(algorithm_id=algorithm_id).delete()
            self.__commit__()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            log(e)
            return None
        return 'ok'

    # Удаление вопросов.
    def remove_results(self, algorithm_id):
        try:
            self.db.session.query(Result).filter_by(algorithm_id=algorithm_id).delete()
            self.__commit__()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            log(e)
            return None
        return 'ok'

    # Сохранение алгоритма.
    def create_or_edit(self, data, contract):
        try:
            algorithm_id = data.get('id')
            if not algorithm_id:
                algorithm = Algorithm()
            else:
                algorithm = self.db.session.query(Algorithm).filter_by(id=algorithm_id).first_or_404()

                if algorithm.creator != contract.clinic_id:
                    return None

            algorithm.title = data.get('title')
            algorithm.creator = data.get('creator')
            algorithm.icon = data.get('icon')
            algorithm.doctor_description = data.get('doctor_description')
            algorithm.patient_description = data.get('patient_description')
            algorithm.depended_algorithms = data.get('depended_algorithms')
            algorithm.keywords = data.get('keywords').split('\n')

            if not algorithm_id:
                self.db.session.add(algorithm)
            self.__commit__()

            self.remove_questions(algorithm.id)
            questions = data.get('questions')
            for q in questions:
                question = Question(algorithm_id=algorithm.id, question_id=q.get('id'),
                                    text=q.get('description'), icon=q.get('icon'),
                                    options=q.get('answers'))
                self.db.session.add(question)

            self.remove_results(algorithm.id)
            results = data.get('results')
            for r in results:
                result = Result(algorithm_id=algorithm.id, result_id=r.get('id'),
                                title=r.get('title'), description=r.get('description'),
                                icon=r.get('icon'), color=r.get('color'),
                                need_warn=r.get('need_warn'), need_response=r.get('need_response'),
                                message=r.get('message'))
                self.db.session.add(result)

            self.__commit__()

            return algorithm
        except Exception as e:
            log(e)
            return None

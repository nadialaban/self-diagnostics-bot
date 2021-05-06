from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


# 1. Алгоритм самодиагностики.
class Algorithm(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    icon = db.Column(db.Text)
    patient_description = db.Column(db.Text)
    doctor_description = db.Column(db.Text)
    creator = db.Column(db.Text)
    keywords = db.Column(db.ARRAY(db.Text))
    depended_algorithms = db.Column(db.ARRAY(db.Integer))
    questions = db.relationship('Question', backref='algorithm')
    results = db.relationship('Result', backref='algorithm')

    def as_short_dict(self):
        alg = {
            'id': self.id,
            'clinic_id': self.creator,
            'title': self.title,
            'icon': self.icon,
            'patient_description': self.patient_description,
            'doctor_description': self.doctor_description,
            'keywords': self.keywords
        }
        return alg

    def as_dict(self):
        alg = {
            'id': self.id,
            'creator': self.creator,
            'title': self.title,
            'icon': self.icon,
            'patient_description': self.patient_description,
            'doctor_description': self.doctor_description,
            'keywords': str.join('\n', self.keywords),
            'depends': False,
            'questions': [q.as_dict() for q in self.questions],
            'results': [r.as_dict() for r in self.results]
        }
        alg['questions'].sort(key=lambda q: q.get('id'))
        return alg


# 2. Вопрос в алгоритме.
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithms.id'))
    question_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    icon = db.Column(db.Text)
    options = db.Column(db.ARRAY(db.JSON))

    def as_dict(self):
        return {
            'id': self.question_id,
            'description': self.text,
            'answers': self.options,
            'icon': self.icon
        }


# 3. Исход.
class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithms.id'))
    result_id = db.Column(db.Integer)
    title = db.Column(db.Text)
    icon = db.Column(db.Text)
    description = db.Column(db.Text)
    color = db.Column(db.Text)
    need_warn = db.Column(db.Boolean)
    need_response = db.Column(db.Boolean)
    message = db.Column(db.Text)

    def as_dict(self):
        return {
            'id': self.result_id,
            'title': self.title,
            'description': self.description,
            'color': self.color,
            'need_warn': self.need_warn,
            'need_response': self.need_response,
            'message': self.message,
            'icon': self.icon
        }


# 4. Контракт.
class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    clinic_id = db.Column(db.Integer)
    algorithms = db.Column(db.ARRAY(db.Integer))

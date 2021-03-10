import json
from flask import Flask, request, render_template
from config import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
import requests
import nltk
from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
from pyaspeller import YandexSpeller

app = Flask(__name__)
speller = YandexSpeller()
mystem = Mystem(MYSTEM)
russian_stopwords = stopwords.words("russian")
icons = {}

# 1. Оисание работы с базой данных.
# 1.1. Подключение к бд.
db_string = "postgres://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
engine = create_engine(db_string)

# 1.2. Описание моделей.
# 1.2.1. Алгоритм.
class Algorithm(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    icon = db.Column(db.Text)
    description = db.Column(db.Text)
    creator = db.Column(db.Text)
    is_used = db.Column(db.Boolean)
    keywords = db.Column(db.ARRAY(db.Text))
    questions = db.relationship('Question', backref='algorithm')
    results = db.relationship('Result', backref='algorithm')


# 1.2.2. Вопрос.
class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithms.id'))
    question_id = db.Column(db.Integer)
    text = db.Column(db.Text)
    icon = db.Column(db.Text)
    answers = db.Column(db.ARRAY(db.Text))
    next_states = db.Column(db.ARRAY(db.Text))


# 1.2.3. Исход.
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


# 1.2.4. Контракт.
class Contract(db.Model):
    __tablename__ = 'contracts'
    contract_id = db.Column(db.Text, primary_key=True)
    clinic_id = db.Column(db.Text)
    algorithms = db.Column(db.ARRAY(db.Integer))


# 1.3. Работа с БД.
# 1.3.1. Получение состояния.
def get_state(state_type, algorithm_id, state_id):
    algorithm = Algorithm.query.filter_by(id=algorithm_id).first()
    if state_type == 'q':
        return next(s for s in algorithm.questions if s.question_id == state_id)
    elif state_type == 'r':
        return next(s for s in algorithm.results if s.result_id == state_id)
    elif state_type == 'a':
        return get_state('q', algorithm_id, 1)
    return 'unexpected type'


# 1.3.2. Получение контракта.
def get_contract(contract_id):
    contract = Contract.query.filter_by(contract_id=str(contract_id)).first()
    return contract


# 1.3.3. Добавление контракта.
def add_contract(contract_id, clinic_id, algorithms=None):
    if algorithms is None:
        algorithms = []
    contract = Contract(contract_id=str(contract_id), clinic_id=str(clinic_id), algorithms=algorithms)
    try:
        db.session.add(contract)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        if str(e.__dict__['orig'].__class__).__contains__('UndefinedTable'):
            db.create_all()
            add_contract(contract_id, clinic_id, algorithms)
        if str(e.__dict__['orig'].__class__).__contains__('UniqueViolation'):
            return 'this contact already exists'
        print(e)
        return 'error'
    return 'ok'


# 1.3.4. Удаление контракта.
def del_contract(contract_id):
    try:
        db.session.query(Contract).filter_by(contract_id=str(contract_id)).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        return 'error'
    return 'ok'


# 1.3.5. Обновление контракта.
def update_contract(contract, algorithms):
    try:
        contract.algorithms = algorithms
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        return 'error'
    return 'ok'


# 1.4. Получение временного токена для ответного запроса.
def get_agent_token(contract_id):
    data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
    }

    try:
        answer = requests.post(MAIN_HOST + '/api/agents/token', json=data).json()
        return answer['agent_token']
    except Exception as e:
        print('connection error', e)


# 2. Описание работы интеллектуального агента
# 2.1. Проверка подключения
@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


# 2.2. Обязательные методы
# 2.2.1. Подключение канала консультирования
@app.route('/init', methods=['POST'])
def init():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    return add_contract(data['contract_id'], data['clinic_id'])


# 2.2.2. Отключение канала консультирования
@app.route('/remove', methods=['POST'])
def remove():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    return del_contract(data['contract_id'])


# 2.2.3. Проверка того, что бот работает.
@app.route('/status', methods=['POST'])
def status():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'
    contracts = Contract.query().all()
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": [int(contract.contract_id) for contract in contracts]
    }

    return json.dumps(answer)


# 2.2.4. Настройки.
# 2.2.4.1. Меню настроек.
@app.route('/settings', methods=['GET'])
def settings():
    key = request.args.get('api_key', APP_KEY)
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)
    agent_token = get_agent_token(contract_id)

    check = check_data(contract, key)
    if check != 'ok':
        return check

    algorithms = Algorithm.query.filter_by(creator='').all()
    algorithms.extend(Algorithm.query.filter_by(creator=contract.clinic_id).all())

    info = []
    for algorithm in algorithms:
        info.append({
            'id': algorithm.id,
            'title': algorithm.title,
            'description': algorithm.description,
            'can_edit': algorithm.creator == contract.clinic_id,
        })

    page_data = {
        'algorithms': info,
        'allowed_algorithms': contract.algorithms,
        'contract_id': contract_id
    }

    return render_template('settings.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.2.4.2. Сохранение настроек.
@app.route('/settings', methods=['POST'])
def save_settings():
    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')

    contract = get_contract(contract_id)

    check = check_data(contract, key)
    if check != 'ok':
        return check

    algorithms = Algorithm.query.filter_by(creator='').all()
    algorithms.extend(Algorithm.query.filter_by(creator=contract.clinic_id).all())
    allowed_algorithms = []

    for alg in algorithms:
        if request.form.get(str(alg.id), ''):
            allowed_algorithms.append(alg.id)

    update_contract(contract, allowed_algorithms)

    return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"


# 2.2.5. Обработка нового сообщения от пациента в канале консультирования.
@app.route('/message', methods=['POST'])
def check_message():
    data = request.json
    key = data['api_key']
    contract_id = data['contract_id']
    contract = get_contract(contract_id)

    check = check_data(contract, key)
    if check != 'ok':
        return check

    algorithms = db.session.query(Algorithm).filter(
        Algorithm.id.in_(contract.algorithms)).all()
    detected_algorithms = []
    detected_algorithms_id = []

    preprocessed_message = preprocess_text(data['message']['text'])
    corrected_tokens = speller.spelled(" ".join(preprocessed_message))
    preprocessed_message = preprocess_text(corrected_tokens)
    for alg in algorithms:
        for word in alg.keywords:
            preprocessed_keyword = preprocess_text(word)
            if all(item in preprocessed_message for item in preprocessed_keyword):
                detected_algorithms.append('• {}'.format(alg.title))
                detected_algorithms_id.append(alg.id)
                break

    if len(detected_algorithms) != 0:
        data = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "message": {
                "text": "Попробуйте пройти один из следующих сценариев самодиагностики, пока ожидаете ответ от врача:\n\n{}".format(
                    str.join('\n', detected_algorithms)),
                "action_link": "/action_algorithms/" + '_'.join(detected_algorithms_id),
                "action_name": "Самодиагностика",
                "only_doctor": False,
                "only_patient": True
            }
        }

        try:
            requests.post(MAIN_HOST + '/api/agents/message', json=data)
        except Exception as e:
            print('connection error', e)

    return "ok"


# 2.3. Основные методы.
# 2.3.1. Выбор алгоритма
@app.route('/action_algorithms', methods=['GET'], defaults={'algorithms': '_'})
@app.route('/action_algorithms/<string:algorithms>', methods=['GET'])
def action_algorithms(algorithms):
    key = request.args.get('api_key', '')
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)
    agent_token = get_agent_token(contract_id)

    check = check_data(contract, key)
    if check != 'ok':
        return check

    recommended_ids = [int(alg_id) for alg_id in algorithms.split('_') if alg_id != '']
    recommended_algorithms = db.session.query(Algorithm).filter(Algorithm.id.in_(recommended_ids)).all()
    algorithms = db.session.query(Algorithm).filter(Algorithm.id.in_(contract.algorithms)).all()

    info = []
    for algorithm in recommended_algorithms:
        if algorithm.icon is None:
            algorithm.icon = 'being-sick'

        info.append({
            'id': algorithm.id,
            'title': algorithm.title,
            'description': algorithm.description,
            'icon': algorithm.icon,
            'recommended': True
        })

    for algorithm in algorithms:
        if algorithm.id not in recommended_ids:
            if algorithm.icon is None:
                algorithm.icon = 'being-sick'

            info.append({
                'id': algorithm.id,
                'title': algorithm.title,
                'description': algorithm.description,
                'icon': algorithm.icon,
                'recommended': False
            })

    db.session.commit()

    page_data = {
        'algorithms': info,
        'contract_id': contract_id
    }

    return render_template('algorithms.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.3.2. Тест
@app.route('/action_test/<int:back>/<int:algorithm_id>/<string:history>', methods=['GET'])
def action_test(back, algorithm_id, history):
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)
    agent_token = get_agent_token(contract_id)

    check = check_data(contract)
    if check != 'ok':
        return check

    algorithm = algorithm_to_dict(algorithm_id)

    last_ids = []
    last_id = -1
    symptoms = []
    current_state = next(st for st in algorithm['questions'] if st['id'] == 1)
    if history != "_":
        states = history.strip('_').split('_')
        for state in states:
            last_ids.append([int(a) for a in state.split('-')])
            if last_ids[-1][0] != algorithm_id:
                last_id = last_ids[-1][0]
        if back == 1:
            current_state = next(st for st in algorithm['questions'] if st['id'] == last_ids[-1][1])
            history = history.replace(str.join('-', [str(a) for a in last_ids[-1]]) + '_', '')
            last_ids.remove(last_ids[-1])
        symptoms = get_symptoms(last_ids)

    page_data = {
        'algorithm_data': algorithm,
        'symptoms': symptoms,
        'symptoms_string': '',
        'last_ids': last_ids,
        'last_test_id': last_id,
        'first': True,
        'testing': True,
        'current_state': current_state,
        'contract_id': contract_id,
        'history': history
    }
    return render_template('algorithm.html', page_data=page_data, agent_token=agent_token, agent_id=AGENT_ID)


# 2.3.3. Завершение сценария
@app.route('/action_test/<int:back>/<int:algorithm_id>/<string:history>', methods=['POST'])
def action_finish(back, algorithm_id, history):
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)
    result_id = request.form.get('result_id', '')
    symptoms = request.form.get('symptoms', '')

    check = check_data(contract)
    if check != 'ok':
        return check

    result = get_state('r', int(algorithm_id), int(result_id))
    send_result(contract_id, result, symptoms)

    return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"


# 2.3.4. Редактирование алгоритма
# 2.3.4.1. Страница редактирования
@app.route('/action_edit/<int:algorithm_id>', methods=['GET'])
def action_edit(algorithm_id):
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)
    agent_token = get_agent_token(contract_id)

    check = check_data(contract)
    if check != 'ok':
        return check

    clinic_id = contract.clinic_id
    all_algorithms = Algorithm.query.filter_by(creator='').all()
    all_algorithms.extend(Algorithm.query.filter_by(creator=clinic_id).all())
    algorithms = []


    for algorithm in all_algorithms:
        if algorithm.id != algorithm_id:
            algorithms.append(['a-'+str(algorithm.id), algorithm.title])
    page_data = {
        'contract_id': contract_id,
        'algorithms': algorithms,
        'message': ' ',
        'algorithm_data': {},
        'icons': icons
    }

    if algorithm_id == 0:
        page_data['algorithm_data'] = {
            'id': algorithm_id,
            'can_delete': False,
            'title': '',
            'icon': 'human-head',
            'description': '',
            'keywords': '',
            'questions': [{
                'id': 1,
                'text': '',
                'icon': 'communication',
                'answers': ['Да', 'Нет'],
                'next_states': ['', '']
            }],
            'results': [{
                'id': 1,
                'title': '',
                'icon': 'health-book',
                'description': '',
                'color': 'grey',
                'need_warn': False,
                'need_response': False,
                'message': ''
            }]
        }
    else:
        page_data['algorithm_data'] = algorithm_to_dict(algorithm_id)

    return render_template('edit_algorithm.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.3.4.1. Сохранение и удаление алгоритма
@app.route('/action_edit/<int:algorithm_id>', methods=['POST'])
def action_save(algorithm_id):
    contract_id = request.args.get('contract_id', '')
    contract = get_contract(contract_id)

    check = check_data(contract)
    if check != 'ok':
        return check

    if algorithm_id != 0:
        algorithm = Algorithm.query.filter_by(id=algorithm_id).first()
        db.session.query(Question).filter_by(algorithm_id=algorithm_id).delete()
        db.session.query(Result).filter_by(algorithm_id=algorithm_id).delete()
        if request.form.get('delete', ''):
            db.session.query(Algorithm).filter_by(id=algorithm_id).delete()
            db.session.commit()
            return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"
        db.session.commit()
    else:
        algorithm = Algorithm()

    algorithm.creator = contract.clinic_id
    algorithm.icon = request.form.get('icon-a', '')
    algorithm.title = request.form.get('title', '')
    algorithm.description = request.form.get('description', '')
    keywords = request.form.get('keywords', '').split('\n')
    algorithm.keywords = [kw.replace('\r', '') for kw in keywords]
    try:
        algorithm.keywords.remove('')
    except:
        pass

    db.session.add(algorithm)
    db.session.commit()

    i = 1
    while request.form.get('q-{}-text'.format(i), ''):
        q = Question(algorithm_id=algorithm.id,
                     question_id=i,
                     text=request.form.get('q-{}-text'.format(i), ''),
                     icon=request.form.get('icon-q-{}'.format(i), 'communication'))
        answers = []
        next_states = []
        j = 1

        while request.form.get('q-{}-a-{}'.format(i, j), ''):
            answers.append(request.form.get('q-{}-a-{}'.format(i, j), ''))
            ns = request.form.get('q-{}-ns-{}'.format(i, j), '')
            next_states.append(ns)
            j += 1
        q.next_states = next_states
        q.answers = answers
        db.session.add(q)
        i += 1

    i = 1
    while request.form.get('r-{}-title'.format(i), ''):
        res = Result(result_id=i,
                     algorithm_id=algorithm.id,
                     title=request.form.get('r-{}-title'.format(i), ''),
                     description=request.form.get('r-{}-description'.format(i), ''),
                     color=request.form.get('r-{}-color'.format(i), ''),
                     need_warn=request.form.get('r-{}-nw'.format(i), '') != '',
                     need_response=request.form.get('r-{}-nr'.format(i), '') != '',
                     message=request.form.get('r-{}-message'.format(i), ''),
                     icon=request.form.get('icon-r-{}'.format(i), 'health-book'))
        db.session.add(res)
        i += 1

    db.session.commit()

    return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"


# 3. Вспомогательльные методы
# 3.1. Отправка сообщения с результом в канал
def send_result(contract_id, result, symptoms):
    patient_text = 'Вами был пройден сценарий самодиагностики <strong>"{}"</strong>.\n\n<strong>Результат:</strong>\n{}.\n\n{}'.format(
        result.algorithm.title, result.title, result.description)
    doctor_data = {}
    if result.need_warn:
        patient_text += '\n\nМы направили уведомление Вашему лечащему врачу.'
        doctor_text = 'Вашим пациентом был пройден сценарий самодиагностики "{}".\n\n' \
                      '<strong>Результат:</strong>\n{}.\n\n{}\n\n' \
                      '<strong>Были получены следующие ответы:</strong>\n{}'.format(result.algorithm.title,
                                                                                    result.title, result.message,
                                                                                    symptoms)
        if result.need_response:
            patient_text += ' Он свяжется с Вами в ближайшее время.'

        doctor_data = {
            "contract_id": contract_id,
            "api_key": APP_KEY,
            "message": {
                "text": doctor_text,
                "only_doctor": True,
                "is_urgent": result.color == 'red',
                "need_answer": result.need_response
            }
        }

    patient_data = {
        "contract_id": contract_id,
        "api_key": APP_KEY,
        "message": {
            "text": patient_text,
            "only_patient": True,
            "is_urgent": result.color == 'red'
        }
    }

    try:
        requests.post(MAIN_HOST + '/api/agents/message', json=patient_data)
        if result.need_warn:
            requests.post(MAIN_HOST + '/api/agents/message', json=doctor_data)
        print('sent to ' + contract_id)
    except Exception as e:
        print('connection error', e)


# 3.2. Перенос данных из JSON в БД
def load():
    global icons
    try:
        with open('data.json', 'r') as f:
            contracts = json.load(f)
        for contract in contracts.keys():
            add_contract(contract, contracts[contract]['clinic_id'], contracts[contract]['algorithms'])
    except:
        pass

    try:
        with open('icons.json', 'r') as f:
            icons = json.load(f)
    except:
        pass


# 3.3. Проверка токенов.
def check_data(contract, key=APP_KEY):
    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract is None:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."
    return 'ok'


# 3.4. Формирование словаря из алгоритма
def algorithm_to_dict(algorithm_id):
    algorithm = Algorithm.query.filter_by(id=algorithm_id).first()
    if algorithm.icon is None:
        algorithm.icon = 'being-sick'
    algorithm_data = {
        'id': algorithm_id,
        'title': algorithm.title,
        'icon': algorithm.icon,
        'description': algorithm.description,
        'can_delete': not algorithm.is_used,
        'keywords': str.join('\n', algorithm.keywords),
        'questions': [],
        'results': [],
        'algorithms': []
    }

    for i in range(len(algorithm.questions)):
        if algorithm.questions[i].icon is None:
            algorithm.questions[i].icon = 'communication'

        question = {
            'id': algorithm.questions[i].question_id,
            'text': algorithm.questions[i].text,
            'answers': algorithm.questions[i].answers,
            'next_states': algorithm.questions[i].next_states,
            'icon': algorithm.questions[i].icon,
            'first': i == 0
        }
        algorithm_data['questions'].append(question)

    for i in range(len(algorithm.results)):
        if algorithm.results[i].icon is None:
            algorithm.results[i].icon = 'health-book'

        res = {
            'id': algorithm.results[i].result_id,
            'title': algorithm.results[i].title,
            'description': algorithm.results[i].description,
            'color': algorithm.results[i].color,
            'alert_type': '',
            'need_warn': algorithm.results[i].need_warn,
            'need_response': algorithm.results[i].need_response,
            'message': algorithm.results[i].message,
            'icon': algorithm.results[i].icon,
            'last': True
        }
        algorithm_data['results'].append(res)

    algorithm_data['questions'].sort(key=lambda q: q.get('id'))
    algorithm_data['results'].sort(key=lambda r: r.get('id'))

    return algorithm_data


# 3.5. Формирование истории ответов
def get_symptoms(states):
    symptoms = []
    if len(states) != 0:
        current_id = states[0][0]
        current_alg = Algorithm.query.filter_by(id=current_id).first()
        for state in states:
            if state[0] != current_id:
                current_alg = Algorithm.query.filter_by(id=state[0]).first()
            q = next(s for s in current_alg.questions if s.question_id == state[1])
            symptoms.append('<strong>Вопрос:</strong> ' + q.text + '<br><strong>Ответ:</strong> ' + q.answers[state[2]])
    return symptoms


# 3.6. Preprocess function
def preprocess_text(text):
    # Tокенизирую
    text = text.lower()
    tokens = mystem.lemmatize(text)
    # Убираю все лишнее
    tokens = [token for token in tokens if token not in russian_stopwords
              and token != " " and token.strip() not in punctuation]

    return tokens


# 4. Запуск
load()

try:
    engine.execute('ALTER TABLE questions ADD COLUMN icon varchar(255)')
    engine.execute("ALTER TABLE results ADD COLUMN icon varchar(255)")
    engine.execute("ALTER TABLE algorithms ADD COLUMN icon varchar(255)")
except Exception as e:
    pass

if __name__ == '__main__':
    load()
    app.run(debug=False, host=HOST, port=PORT)

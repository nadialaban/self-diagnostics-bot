import json
from flask import Flask, request, render_template, url_for
from config import *
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
contracts = {}

# 1. Оисание работы с базой данных.
# 1.1. Подключение к бд.
db_string = "postgres://{}:{}@{}:{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# 1.2. Описание моделей.
# 1.2.1. Алгоритм.
class Algorithm(db.Model):
    __tablename__ = 'algorithms'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
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
    answers = db.Column(db.ARRAY(db.Text))
    next_states = db.Column(db.ARRAY(db.Text))


# 1.2.3. Исход.
class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    algorithm_id = db.Column(db.Integer, db.ForeignKey('algorithms.id'))
    result_id = db.Column(db.Integer)
    title = db.Column(db.Text)
    description = db.Column(db.Text)
    color = db.Column(db.Text)
    need_warn = db.Column(db.Boolean)
    need_response = db.Column(db.Boolean)
    message = db.Column(db.Text)


# 1.3. Получение заданного состояния.
def get_state(state_type, algorithm_id, state_id):
    algorithm = Algorithm.query.filter_by(id=algorithm_id).first()
    if state_type == 'q':
        return next(s for s in algorithm.questions if s.question_id == state_id)
    elif state_type == 'r':
        return next(s for s in algorithm.results if s.result_id == state_id)
    elif state_type == 'a':
        return get_state('q', algorithm_id, 1)
    return 'unexpected type'


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

    contract_id = str(data['contract_id'])
    if contract_id not in contracts:
        contracts.update({
            contract_id: {
                'algorithms': [],
                'clinic_id': str(data['clinic_id'])
            }})
        save()

    return 'ok'


# 2.2.2. Отключение канала консультирования
@app.route('/remove', methods=['POST'])
def remove():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    contract_id = str(data['contract_id'])
    if contract_id in contracts:
        del contracts[contract_id]
    save()

    return 'ok'


# 2.2.3. Проверка того, что бот работает.
@app.route('/status', methods=['POST'])
def status():
    data = request.json

    if data['api_key'] != APP_KEY:
        return 'invalid key'

    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": [int(contract_id) for contract_id in contracts]
    }

    return json.dumps(answer)


# 2.2.4. Настройки.
# 2.2.4.1. Меню настроек.
@app.route('/settings', methods=['GET'])
def settings():
    key = request.args.get('api_key', APP_KEY)
    contract = request.args.get('contract_id', '')
    clinic_id = str(contracts[contract]['clinic_id'])
    agent_token = get_agent_token(contract)

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    algorithms = Algorithm.query.filter_by(creator='').all()
    algorithms.extend(Algorithm.query.filter_by(creator=clinic_id).all())


    info = []
    for algorithm in algorithms:
        info.append({
            'id': algorithm.id,
            'title': algorithm.title,
            'description': algorithm.description,
            'can_edit': algorithm.creator == clinic_id,
        })

    page_data = {
        'algorithms': info,
        'allowed_algorithms': contracts[contract]['algorithms'],
        'contract_id': contract
    }

    return render_template('settings.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.2.4.2. Сохранение настроек.
@app.route('/settings', methods=['POST'])
def save_settings():
    key = request.args.get('api_key', '')
    contract = request.args.get('contract_id', '')
    clinic_id = str(contracts[contract]['clinic_id'])

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    algorithms = Algorithm.query.filter_by(creator='').all()
    algorithms.extend(Algorithm.query.filter_by(creator=clinic_id).all())
    allowed_algorithms = []

    for alg in algorithms:
        if request.form.get(str(alg.id), ''):
            allowed_algorithms.append(alg.id)

    contracts[contract].update({'algorithms': allowed_algorithms})
    save()

    return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"


# 2.2.5. Обработка нового сообщения от пациента в канале консультирования.
@app.route('/message', methods=['POST'])
def check_message():
    data = request.json

    if data['api_key'] != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if str(data['contract_id']) not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    algorithms = db.session.query(Algorithm).filter(
        Algorithm.id.in_(contracts[str(data['contract_id'])]['algorithms'])).all()
    detected_algorithms = []

    for alg in algorithms:
        for word in alg.keywords:
            if word.lower() in data['message']['text'].lower():
                detected_algorithms.append('• {}'.format(alg.title))
                break

    if len(detected_algorithms) != 0:
        data = {
            "contract_id": data['contract_id'],
            "api_key": APP_KEY,
            "message": {
                "text": "Попробуйте пройти один из следующих сценариев самодиагностики, пока ожидаете ответ от врача:\n\n{}".format(
                    str.join('\n', detected_algorithms)),
                "action_link": "/action_algorithms",
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
@app.route('/action_algorithms', methods=['GET'])
def action_algorithms():
    key = request.args.get('api_key', '')
    contract_id = str(request.args.get('contract_id', ''))
    agent_token = get_agent_token(contract_id)

    if key != APP_KEY:
        return "<strong>Некорректный ключ доступа.</strong> Свяжитесь с технической поддержкой."
    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    algorithms = db.session.query(Algorithm).filter(Algorithm.id.in_(contracts[contract_id]['algorithms'])).all()

    info = []
    for algorithm in algorithms:
        info.append({
            'id': algorithm.id,
            'title': algorithm.title,
            'description': algorithm.description,
        })

    page_data = {
        'algorithms': info,
        'contract_id': contract_id
    }

    return render_template('algorithms.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.3.2. Тест
@app.route('/action_test/<int:algorithm_id>/<string:history>', methods=['GET'])
def action_test(algorithm_id, history):
    contract_id = str(request.args.get('contract_id', ''))
    back = str(request.args.get('back', ''))
    agent_token = get_agent_token(contract_id)

    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

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
        if back != '':
            current_state = next(st for st in algorithm['questions'] if st['id'] == last_ids[-1][1])
            history = history.replace(str.join('-',[str(a) for a in last_ids[-1]])+'_', '')
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
@app.route('/action_test/<int:algorithm_id>/<string:history>', methods=['POST'])
def action_finish(algorithm_id, history):
    contract_id = request.args.get('contract_id', '')
    result_id = request.form.get('result_id', '')
    symptoms = request.form.get('symptoms', '')

    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    result = get_state('r', int(algorithm_id), int(result_id))
    send_result(contract_id, result, symptoms)

    return "<strong>Спасибо, окно можно закрыть</strong><script>window.parent.postMessage('close-modal-success','*');</script>"


# 2.3.4. Редактирование алгоритма
# 2.3.4.1. Страница редактирования
@app.route('/action_edit/<int:algorithm_id>', methods=['GET'])
def action_edit(algorithm_id):
    contract_id = request.args.get('contract_id', '')
    clinic_id = str(contracts[contract_id]['clinic_id'])
    agent_token = get_agent_token(contract_id)

    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

    all_algorithms = Algorithm.query.filter_by(creator='').all()
    all_algorithms.extend(Algorithm.query.filter_by(creator=clinic_id).all())
    algorithms = []

    for algorithm in all_algorithms:
        algorithms.append(algorithm.title)

    page_data = {
        'contract_id': contract_id,
        'algorithms': algorithms,
        'message': ' ',
        'algorithm_data': {}
    }

    if algorithm_id == 0:
        page_data['algorithm_data'] = {
            'id': algorithm_id,
            'can_delete': False,
            'title': '',
            'description': '',
            'keywords': '',
            'questions': [{
                'id': 1,
                'text': '',
                'answers': ['Да', 'Нет'],
                'next_states': ['', '']
            }],
            'results': [{
                'id': 1,
                'title': '',
                'description': '',
                'color': '',
                'need_warn': False,
                'need_response': False,
                'message': ''
            }]
        }
    else:
        page_data['algorithm_data'] = algorithm_to_dict(algorithm_id)
        page_data['algorithms'].remove(page_data['algorithm_data']['title'])

    return render_template('edit_algorithm.html', page_data=page_data, agent_id=AGENT_ID, agent_token=agent_token)


# 2.3.4.1. Сохранение и удаление алгоритма
@app.route('/action_edit/<int:algorithm_id>', methods=['POST'])
def action_save(algorithm_id):
    contract_id = request.args.get('contract_id', '')

    if contract_id not in contracts:
        return "<strong>Запрашиваемый канал консультирования не найден.</strong> Попробуйте отключить и заново подключить интеллектуального агента. Если это не сработает, свяжитесь с технической поддержкой."

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

    algorithm.creator = contracts[contract_id]['clinic_id']
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
                     text=request.form.get('q-{}-text'.format(i), ''))
        answers = []
        next_states = []
        j = 1

        while request.form.get('q-{}-a-{}'.format(i, j), ''):
            answers.append(request.form.get('q-{}-a-{}'.format(i, j), ''))
            ns = request.form.get('q-{}-ns-{}'.format(i, j), '')
            if ns[0] == 'с':
                alg = Algorithm.query.filter_by(title=str.join('"', ns.split('"')[1:-1])).first()
                alg.is_used = True
                next_states.append('a-{}'.format(alg.id))
            else:
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
                     message=request.form.get('r-{}-message'.format(i), ''))
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


# 3.2. Загрузка данных
def load():
    global contracts
    try:
        with open('data.json', 'r') as f:
            contracts = json.load(f)
    except:
        save()


# 3.3. Сохранение данных
def save():
    global contracts
    with open('data.json', 'w') as f:
        json.dump(contracts, f, indent=6)


# 3.4. Формирование словаря из алгоритма
def algorithm_to_dict(algorithm_id):
    algorithm = Algorithm.query.filter_by(id=algorithm_id).first()
    algorithm_data = {
        'id': algorithm_id,
        'title': algorithm.title,
        'description': algorithm.description,
        'can_delete': not algorithm.is_used,
        'keywords': str.join('\n', algorithm.keywords),
        'questions': [],
        'results': [],
        'algorithms': []
    }

    for i in range(len(algorithm.questions)):
        question = {
            'id': algorithm.questions[i].question_id,
            'text': algorithm.questions[i].text,
            'answers': algorithm.questions[i].answers,
            'next_states': algorithm.questions[i].next_states,
            'first': i == 0
        }
        algorithm_data['questions'].append(question)

    for i in range(len(algorithm.results)):
        res = {
            'id': algorithm.results[i].result_id,
            'title': algorithm.results[i].title,
            'description': algorithm.results[i].description,
            'color': algorithm.results[i].color,
            'need_warn': algorithm.results[i].need_warn,
            'need_response': algorithm.results[i].need_response,
            'message': algorithm.results[i].message,
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

# 4. Запуск
load()

if __name__ == '__main__':
    app.run(debug=False, host=HOST, port=PORT)

from datetime import datetime
from flask import request, abort, jsonify, render_template
from sentry_sdk import capture_exception
import sys, os
import requests
import json

from config import *


# Получение времени в строковом представлении
def gts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S - ")


# Логирование
def log(error, terminating=False):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    if PRODUCTION:
        capture_exception(error)

    if terminating:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error, "CRITICAL")
    else:
        print(gts(), exc_type, fname, exc_tb.tb_lineno, error)


# Проверка аргументов
def verify_args(func):
    def wrapper(*args, **kargs):
        if not request.args.get('contract_id'):
            abort(422)
        if request.args.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.args, request.form, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


# Проверка аргументов в JSON
def verify_json(func):
    def wrapper(*args, **kargs):
        if not request.json.get('contract_id') and "status" not in request.url:
            abort(422)
        if request.json.get('api_key') != API_KEY:
            abort(401)
        try:
            return func(request.json, *args, **kargs)
        except Exception as e:
            log(e, True)
            abort(500)

    wrapper.__name__ = func.__name__
    return wrapper


# Получение интерфейса
def get_ui(contract, mode, state='loading', recommended_algorithms=''):
    agent_token = get_agent_token(contract.id)
    return render_template('index.html', mode=mode, state=state,
                           contract_id=contract.id, clinic_id=contract.clinic_id, agent_id=AGENT_ID,
                           api_host=MAIN_HOST.replace('8001', '8000'), local_host=LOCALHOST,
                           agent_token=agent_token, lc=dir_last_updated('static'),
                           recommended_algorithms=recommended_algorithms)


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))


# Получение токена.
def get_agent_token(contract_id):
    data = {
        "contract_id": contract_id,
        "api_key": API_KEY,
    }

    try:
        answer = requests.post(MAIN_HOST + '/api/agents/token', json=data).json()
        return answer['agent_token']
    except Exception as e:
        print('connection error', e)


# Работа с сообщениями
# Получение сообщения о результате для пациента
def get_patient_message(result, algorithm):
    text = 'Вами был пройден сценарий самодиагностики <strong>"{}"</strong>.\n\n'.format(algorithm)
    text += '<strong>Результат:</strong>\n{}\n\n.'.format(result['title'])
    text += result['description']

    if result['need_warn']:
        text += '\n\nМы направили уведомление Вашему лечащему врачу.'
        if result['need_response']:
            text += ' Он свяжется с Вами в ближайшее время.'

    return text


# Получение сообщения о результате для доктора
def get_doctor_message(result, algorithm, history):
    text = 'Вашим пациентом был пройден сценарий самодиагностики <strong>"{}"</strong>.\n\n'.format(algorithm)
    text += '<strong>Результат:</strong>\n{}\n\n.'.format(result['title'])
    if result['need_warn']:
        text += '{}\n\n'.format(result['message'])
    else:
        text += '"{}"\n\n'.format(result['description'])

    history = ['<strong>Вопрос:</strong> {}\n<strong>Ответ:</strong> {}'.format(h['description'], h['answer']) for h in history]
    text += '<strong>Были получены следующие ответы:</strong>\n{}'.format('\n\n'.join(history))

    return text

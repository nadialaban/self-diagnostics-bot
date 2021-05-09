from config import *
from manage import *
from helpers import *

from managers.AlgorithmManager import AlgorithmManager
from managers.ContractManager import ContractManager
from message_checker import MessageChecker
from medsenger_api import AgentApiClient
from flask import Flask, request, render_template

import requests


medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)

contract_manager = ContractManager(medsenger_api, db)
algorithm_manager = AlgorithmManager(medsenger_api, db)
message_checker = MessageChecker(medsenger_api, algorithm_manager)


# 1. Проверка подключения.
@app.route('/', methods=['GET'])
def index():
    return 'waiting for the thunder!'


@app.route('/order', methods=['POST'])
@verify_json
def order(data):
    pass


# 2 Обязательные методы Интеллектуального агента.
# 2.1. Подключение канала консультирования.
@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract_id = data.get('contract_id')
    clinic_id = data.get('clinic_id')
    if not contract_id:
        abort(422)

    return contract_manager.add(contract_id, clinic_id)


# 2.2. Отключение канала консультирования.
@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    contract_id = data.get('contract_id')

    if not contract_id:
        abort(422)

    return contract_manager.remove(contract_id)


# 2.3. Проверка того, что агент работает.
@app.route('/status', methods=['POST'])
@verify_json
def status(data):
    if data.get('api_key') != API_KEY:
        return 'invalid key'

    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": contract_manager.get_active_contracts()
    }

    return json.dumps(answer)


# 2.4. Обработка нового сообщения от пациента в канале консультирования.
@app.route('/message', methods=['POST'])
@verify_json
def check_message():
    data = request.json
    contract_id = data.get('contract_id')
    contract = contract_manager.get(contract_id)

    print(data)
    detected_algorithms = message_checker.check(contract, data['message']['text'])

    if len(detected_algorithms) != 0:
        text = 'Попробуйте пройти один из следующих сценариев самодиагностики, пока ожидаете ответ от врача:\n\n{}'.format(
            ['\n'.join([a['title'] for a in detected_algorithms])]
        )
        link = '/algorithms/{}'.format('_'.join([a['id'] for a in detected_algorithms]))

        res = medsenger_api.send_message(contract_id, text, action_link=link, action_name='Самодиагностика', only_patient=True)

        return res
    return 'ok'


# 3. Настройки.
# 3.1. Меню настроек.
@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, data):
    contract = contract_manager.get(request.args.get('contract_id', ''))
    return get_ui(contract=contract, mode='admin', state='settings')


# 3.2. Сохранение настроек.
@app.route('/api/settings/save', methods=['POST'])
@verify_args
def save_settings(args, data):
    contract = contract_manager.get(request.args.get('contract_id', ''))
    result = contract_manager.update(contract, request.json.get('recommendations'))
    if result:
        return jsonify({
            "saved_ids": result
        })
    else:
        abort(404)


# 4. Редактор
# 4.1. Удаление алгоритма
@app.route('/api/settings/delete_algorithm', methods=['POST'])
@verify_args
def delete_algorithm(args, algorithm):
    result = algorithm_manager.remove(request.json.get('id'))

    if result:
        return jsonify({
            "deleted_id": result
        })
    else:
        abort(404)


# 4.1. Сохранение алгоритма
@app.route('/api/settings/save_algorithm', methods=['POST'])
@verify_args
def save_algorithm(args, algorithm):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)
    algorithm = algorithm_manager.create_or_edit(request.json, contract)

    if algorithm:
        return jsonify(algorithm.as_dict())
    else:
        abort(422)


# 5. Методы доступа.
# 5.1. Получение списка алгоритмов, доступных клинике.
@app.route('/api/algorithms', methods=['GET'])
@verify_args
def get_algorithms(args, data):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)

    algorithms = algorithm_manager.get_algorithms(contract.clinic_id)
    algorithms.sort(key=lambda alg: alg['clinic_id'] != contract.clinic_id)

    data = {
        'algorithms': algorithms,
        'enabled': contract.algorithms
    }

    if algorithms:
        return jsonify(data)
    else:
        abort(422)


# 5.2. Получение списка алгоритмов, доступных пациенту.
@app.route('/api/enabled_algorithms', methods=['GET'], defaults={'recommended': ''})
@app.route('/api/enabled_algorithms/<string:recommended>', methods=['GET'])
@verify_args
def get_enabled_algorithms(args, data, recommended):
    contract_id = args.get('contract_id')
    contract = contract_manager.get(contract_id)

    algorithms = algorithm_manager.get_enabled_algorithms(contract)

    recommendations = [int(alg) for alg in recommended.split('_')] if recommended != '' else []
    algorithms.sort(key=lambda alg: alg['id'] not in recommendations)

    data = {
        'algorithms': algorithms
    }

    if algorithms:
        return jsonify(data)
    else:
        abort(422)


# 5.3. Получение алгоритма.
@app.route('/api/algorithm/<int:algorithm_id>', methods=['GET'])
@verify_args
def get_algorithm(args, data, algorithm_id):
    algorithm = algorithm_manager.get(algorithm_id)

    if algorithm:
        if algorithm_manager.is_depended_algorithm(algorithm_id):
            algorithm['depends'] = True
        return jsonify(algorithm)
    else:
        abort(422)


# 5.4. Получение описания иконок.
@app.route('/api/icons', methods=['GET'])
@verify_args
def get_icons(args, data):
    icons = {}
    with open('icons.json', 'r') as f:
        icons = json.load(f)
    return jsonify(icons)


# 6. Запуск тестирования.
@app.route('/algorithms', methods=['GET'], defaults={'algorithms': ''})
@app.route('/algorithms/<string:algorithms>', methods=['GET'])
@verify_args
def open_main_menu(args, data, algorithms):
    contract_id = request.args.get('contract_id', '')
    contract = contract_manager.get(contract_id)

    return get_ui(contract=contract, mode='patient', state='main', recommended_algorithms=algorithms)


# 7. Завершение сценария
@app.route('/api/result', methods=['POST'])
@verify_args
def action_finish(args, data):
    data = request.json
    contract_id = request.args.get('contract_id', '')
    contract = contract_manager.get(contract_id)

    result = data['result']
    patient_message = get_patient_message(data['result'], data['algorithm_title'])
    doctor_message = get_doctor_message(data['result'], data['algorithm_title'], data['history'])

    medsenger_api.send_message(contract_id, patient_message, only_patient=True,
                               is_urgent=(result['color'] == 'red'))

    medsenger_api.send_message(contract_id, doctor_message, only_doctor=True,
                               is_urgent=(result['color'] == 'red'), need_answer=result['need_response'])

    return "ok"


# 4. Запуск
if __name__ == '__main__':
    app.run(debug=API_DEBUG, host=HOST, port=PORT)

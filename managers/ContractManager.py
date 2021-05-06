from helpers import log
from sqlalchemy.exc import SQLAlchemyError
from managers.Manager import Manager
from models import Contract


class ContractManager(Manager):
    def __init__(self, *args):
        super(ContractManager, self).__init__(*args)

    # Получение контракта
    def get(self, contract_id):
        return self.db.session.query(Contract).filter_by(id=contract_id).first_or_404()

    # Добавление контракта
    def add(self, contract_id, clinic_id, algorithms=None):
        contract = self.db.session.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            if algorithms is None:
                algorithms = []

            contract = Contract(id=contract_id, clinic_id=clinic_id, algorithms=algorithms)
            self.db.session.add(contract)
            self.__commit__()
        return 'ok'

    # Удаление контракта
    def remove(self, contract_id):
        try:
            self.db.session.query(Contract).filter_by(id=contract_id).delete()
            self.__commit__()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            log(e)
            return None
        return contract_id

    # Обновление контракта.
    def update(self, contract, algorithms):
        try:
            contract.algorithms = algorithms
            self.__commit__()
        except SQLAlchemyError as e:
            self.db.session.rollback()
            log(e)
            return None
        return algorithms

    def get_active_contracts(self):
        contracts = self.db.session.query(Contract).all()
        return [contract.id for contract in contracts]

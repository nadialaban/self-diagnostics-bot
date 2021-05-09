import nltk
from managers.AlgorithmManager import AlgorithmManager
from nltk.corpus import stopwords
from pymystem3 import Mystem
from string import punctuation
from pyaspeller import YandexSpeller
from medsenger_api import AgentApiClient


class MessageChecker:
    def __init__(self, medsenger_api: AgentApiClient, algorithm_manager:AlgorithmManager):
        self.medsenger_api = medsenger_api
        self.algorithm_manager = algorithm_manager

        self.russian_stopwords = stopwords.words("russian")
        self.speller = YandexSpeller()
        self.mystem = Mystem()

    def check(self, contract, message):
        enabled_algorithms = self.algorithm_manager.get_enabled_algorithms(contract)
        detected_algorithms = []

        # print('1')
        msg = self.preprocess_text(message)
        msg = self.spellcheck(msg)

        # print('2')
        for alg in enabled_algorithms:
            for word in alg['keywords']:
                preprocessed_keyword = self.preprocess_text(word)
                if all(item in msg for item in preprocessed_keyword):
                    detected_algorithms.append({'title':  alg['title'], 'id': str(alg['id'])})
                    break

        return detected_algorithms

    # Коррекция опечаток
    def spellcheck(self, tokens):
        # Убераю опечатки
        corrected_tokens = self.speller.spelled(" ".join(tokens))
        # Повторно обрабатываю
        preprocessed_message = self.preprocess_text(corrected_tokens)
        return preprocessed_message

    # Предобработка текста
    def preprocess_text(self, text):
        # Tокенизирую
        text = text.lower()
        tokens = self.mystem.lemmatize(text)
        # Убираю все лишнее
        tokens = [token for token in tokens if token not in self.russian_stopwords
                  and token != " " and token.strip() not in punctuation]

        return tokens






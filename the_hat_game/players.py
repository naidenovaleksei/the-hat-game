from collections import namedtuple

import requests

from the_hat_game.loggers import logger

HIDE_WARNINGS = True


PlayerDefinition = namedtuple("PlayerDefinition", ["name", "api"])


class AbstractPlayer:
    def __init__(self):
        raise NotImplementedError()

    def explain(self, word, n_words):
        raise NotImplementedError()

    def guess(self, words, n_words):
        raise NotImplementedError()


class RemotePlayer(AbstractPlayer):
    def __init__(self, url, timeout=1):
        self.url = url
        self.timeout = 1
        self.ping()

    def ping(self):
        try:
            response = requests.get(self.url, timeout=60)
            assert response.status_code == 200
        except Exception as exc:
            if not HIDE_WARNINGS:
                logger.warn(exc)

    def explain(self, word, n_words):
        try:
            response = requests.get(
                self.url + "/explain",
                {"word": word, "n_words": n_words},
                timeout=self.timeout,
            )
            word_list = response.json()
        except Exception as exc:
            if not HIDE_WARNINGS:
                logger.warning(exc)
            word_list = []
        return word_list

    def guess(self, words, n_words):
        try:
            response = requests.get(
                self.url + "/guess",
                {"words": words, "n_words": n_words},
                timeout=self.timeout,
            )
            response_time = response.elapsed.total_seconds()
            response_code = response.status_code
            word_list = response.json()
        except Exception as exc:
            if not HIDE_WARNINGS:
                logger.warning(exc)
            word_list = []
            response_time = 0
            response_code = None
        return {"word_list": word_list, "time": response_time, "code": response_code}

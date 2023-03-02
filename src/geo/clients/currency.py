"""
Функции для взаимодействия с внешним сервисом-провайдером данных о курсах валют.
"""
from http import HTTPStatus
from typing import Optional

import httpx

from app.settings import REQUESTS_TIMEOUT, API_KEY_APILAYER
from base.clients.base import BaseClient
from geo.clients.shemas import CurrencyRatesDTO


class CurrencyClient(BaseClient):
    """
    Реализация функций для взаимодействия с внешним сервисом-провайдером данных о курсах валют.
    """

    def get_base_url(self) -> str:
        return "https://api.apilayer.com/fixer/latest"

    def _request(self, endpoint: str) -> Optional[dict]:
        with httpx.Client(timeout=REQUESTS_TIMEOUT) as client:
            headers = {"apikey": API_KEY_APILAYER}
            response = client.get(endpoint, headers=headers)
            if response.status_code == HTTPStatus.OK:
                return response.json()

            return None

    def get_currency_rates(self, code: str) -> Optional[CurrencyRatesDTO]:
        """
        Получение данных о курсах валют.

        :param code: трехзначный код валюты
        :return:
        """

        if responce := self._request(f"{self.get_base_url()}?base={code}"):
            return CurrencyRatesDTO(
                base=responce["base"],
                date=responce["date"],
                rates=responce["rates"]
            )

        return None
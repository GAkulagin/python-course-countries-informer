from typing import Optional

from django.db.models import Q, QuerySet

from geo.clients.currency import CurrencyClient
from geo.clients.shemas import CurrencyRatesDTO
from geo.models import CurrencyRate


class CurrencyService:
    """
    Сервис для работы с данными о курсах валют.
    """

    def get_currency_rates(self, code: str) -> QuerySet[CurrencyRate]:
        """
        Получение курсов валют по отношению к указанной валюте.

        :param code: трехзначный код валюты
        :return:
        """

        currency_rates = CurrencyRate.objects.filter(Q(base__iregex=code))

        if not currency_rates:
            if data := CurrencyClient().get_currency_rates(code):
                for key, value in data.rates.items():
                    self.build_currency_model(data.base, data.date, key, value)
                currency_rates = CurrencyRate.objects.filter(Q(base__iregex=code))

        return currency_rates

    def build_currency_model(self, base: str, date: str, compared: str, value: float) -> CurrencyRate:
        """
        Создание модели CurrencyRate

        :param base: Валюта.
        :param date: Дата получения курса.
        :param compared: валюта для сравнения.
        :param value: курс base к compared.
        :return:
        """

        return CurrencyRate.objects.create(
            base=base,
            date=date,
            compared_to=compared,
            value=value,
        )
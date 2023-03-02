from typing import Optional, Dict

from django.db.models import Q, QuerySet
from django.db.models.functions import Lower

from geo.clients.geo import GeoClient
from geo.clients.shemas import CountryDTO
from geo.models import Country


class CountryService:
    """
    Сервис для работы с данными о странах.
    """

    def get_all_countries(self) -> QuerySet[Country]:
        """
        Получение списка всех стран в базе данных.

        :return:
        """
        return Country.objects.all()

    def get_countries(self, name: str) -> QuerySet[Country]:
        """
        Получение списка стран по названию.

        :param name: Название страны
        :return:
        """

        countries = Country.objects.filter(
            Q(name__iregex=name) | Q(demonym__iregex=name)
        )
        if not countries:
            # если страна не найдена в БД, то – поиск в API и сохранение в БД
            if countries_data := GeoClient().get_countries(name):
                Country.objects.bulk_create(
                    [self.build_model(country) for country in countries_data],
                    batch_size=1000,
                )
                # поиск нужной страны в БД после импорта новых стран
                countries = Country.objects.filter(
                    Q(name__iregex=name) | Q(demonym__iregex=name)
                )

        return countries

    @staticmethod
    def get_countries_codes() -> Optional[Dict[str, int]]:
        """
        Получение списка ISO Alpha2 кодов стран.

        :param name: Название страны
        :return:
        """

        if (
            data := Country.objects.filter(alpha2code__isnull=False)
            .annotate(alpha2code_lower=Lower("alpha2code"))
            .values("pk", "alpha2code_lower")
        ):
            return {item["alpha2code_lower"]: item["pk"] for item in data}

        return None

    @staticmethod
    def get_countries_by_codes(codes: set[str]) -> QuerySet:
        """
        Получение списка стран по их ISO Alpha2 кодам.

        :param codes: Множество ISO Alpha2 кодов стран.
        :return:
        """

        alpha2codes = [code.lower() for code in codes]

        return (
            Country.objects.annotate(alpha2code_lower=Lower("alpha2code"))
            .filter(alpha2code_lower__in=alpha2codes)
            .all()
        )

    def build_model(self, country: CountryDTO) -> Country:
        """
        Формирование объекта модели страны.

        :param CountryDTO country: Данные о стране.
        :return:
        """

        return Country(
            alpha3code=country.alpha3code,
            name=country.name,
            alpha2code=country.alpha2code,
            capital=country.capital,
            region=country.region,
            subregion=country.subregion,
            population=country.population,
            latitude=country.latitude,
            longitude=country.longitude,
            demonym=country.demonym,
            area=country.area,
            numeric_code=country.numeric_code,
            flag=country.flag,
            currencies=[currency.code for currency in country.currencies],
            languages=[language.name for language in country.languages],
        )

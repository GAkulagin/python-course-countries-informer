from typing import Set

from django.db.models import Q, QuerySet
from django.db.models.functions import Lower

from geo.clients.geo import GeoClient
from geo.clients.shemas import CityDTO
from geo.models import Country, City
from geo.services.country import CountryService
from geo.services.shemas import CountryCityDTO


class CityService:
    """
    Сервис для работы с данными о городах.
    """

    def __init__(self) -> None:
        self.geo_client = GeoClient()

    def get_all_cities(self) -> QuerySet[City]:
        """
        Получение списка всех городов в базе данных.

        :return:
        """
        return City.objects.all()

    def get_cities(self, name: str) -> QuerySet[City]:
        """
        Получение списка городов по названию.

        :param name: Название города
        :return:
        """

        cities_db = City.objects.prefetch_related("country").filter(
            Q(name__iregex=name) | Q(region__iregex=name)
        )
        if not cities_db:
            if cities_api := self.geo_client.get_cities(name):
                # если города в базе нет, то нужно его создать
                # перед этим необходимо получить информацию о стране для создания связи города со страной
                country_codes = {city.country.alpha2code for city in cities_api}
                # поиск страны в БД, связанной с искомым городом
                countries = Country.objects.filter(alpha2code__in=country_codes).values(
                    "alpha2code"
                )
                # страны, которые еще не существуют в БД
                # `country_codes` содержит общее множество кодов стран для связи с искомыми городами
                # `countries_to_find` содержит коды стран, которые не нашлись в БД
                if countries_to_find := country_codes - {
                    country["alpha2code"] for country in countries
                }:
                    # получение информации о странах, отсутствующих в БД
                    if countries_to_save := self._find_countries(countries_to_find):
                        self._save_countries(countries_to_save)

                # формирование списка связанных с городами стран
                if countries := Country.objects.filter(
                    alpha2code__in=country_codes
                ).values("pk", "alpha2code"):
                    countries_map = {
                        country["alpha2code"]: country["pk"] for country in countries
                    }
                    cities_to_save = []
                    for city in cities_api:
                        # формирование списка городов для сохранения
                        cities_to_save.append(
                            self.build_model(
                                city, country_id=countries_map[city.country.alpha2code]
                            )
                        )

                    self._save_cities(cities_to_save)

                    # поиск нужной страны в БД после импорта новых городов
                    cities_db = City.objects.prefetch_related("country").filter(
                        Q(name__iregex=name) | Q(region__iregex=name)
                    )

        return cities_db

    @staticmethod
    def get_cities_by_codes(codes: set[CountryCityDTO]) -> QuerySet:
        """
        Получение списка городов по ISO Alpha2 кодам стран и названиям городов.

        :param codes: Множество ISO Alpha2 кодов стран и названий городов.
        :return:
        """

        queries = [
            Q(city_name_lower=code.city) & Q(country_alpha2code_lower=code.alpha2code)
            for code in codes
        ]
        conditions = queries.pop()
        for query in queries:
            conditions |= query

        return (
            City.objects.annotate(
                city_name_lower=Lower("name"),
                country_alpha2code_lower=Lower("country__alpha2code"),
            )
            .filter(conditions)
            .select_related("country")
            .all()
        )

    def build_model(self, city: CityDTO, country_id: int) -> City:
        """
        Формирование объекта модели города.

        :param CityDTO city: Данные о городе.
        :param int country_id: Идентификатор страны в БД.
        :return:
        """

        return City(
            country_id=country_id,  # связь по внешнему ключу
            name=city.name,
            region=city.state_or_region if city.state_or_region else "",
            latitude=city.latitude,
            longitude=city.longitude,
        )

    def _find_countries(self, codes: Set[str]) -> list[Country]:
        """
        Поиск информации о странах в API.

        :param Set[str] codes: Множество ISO Alpha2 кодами стран
        :return:
        """

        country_service = CountryService()
        countries = []
        for code in codes:
            if country := self.geo_client.get_country_by_code(code):
                countries.append(country_service.build_model(country))

        return countries

    def _save_countries(self, countries: list[Country]) -> None:
        """
        Сохранение информации о странах в БД.

        :param Set[Country] countries: Множество с моделями стран
        :return:
        """

        Country.objects.bulk_create(
            countries,
            batch_size=1000,
        )

    def _save_cities(self, cities: list[City]) -> None:
        """
        Сохранение информации о странах в БД.

        :param Set[City] cities: Множество с моделями городов
        :return:
        """

        # сохранение новых городов в БД
        City.objects.bulk_create(
            cities,
            batch_size=1000,
        )

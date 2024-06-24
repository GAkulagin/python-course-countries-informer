"""Представления Django"""
from django.core.cache import caches
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.settings import api_settings

from app.settings import CACHE_WEATHER
from geo.serializers import CountrySerializer, CitySerializer, WeatherSerializer, CurrencySerializer
from geo.services.city import CityService
from geo.services.country import CountryService
from geo.services.currency import CurrencyService
from geo.services.weather import WeatherService

default_pagination = api_settings.DEFAULT_PAGINATION_CLASS
paginator = default_pagination()


@api_view(["GET"])
def get_city(request: Request, name: str) -> JsonResponse:
    """
    Получить информацию о городах по названию.

    Сначала метод ищет данные в БД. Если данные не найдены, то делается запрос к API.
    После получения данных от API они сохраняются в БД.

    :param Request request: Объект запроса
    :param str name: Название города
    :return:
    """

    if cities := CityService().get_cities(name):
        serializer = CitySerializer(cities, many=True)

        return JsonResponse(serializer.data, safe=False)

    raise NotFound


@api_view(["GET"])
def get_cities(request: Request) -> JsonResponse:
    """
    Получение информации о всех городах в базе данных.

    :param Request request: Объект запроса
    :return:
    """

    if cities := CityService().get_all_cities():
        page = paginator.paginate_queryset(cities, request)
        serializer = CitySerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    return JsonResponse([], safe=False)


@api_view(["GET"])
def get_country(request: Request, name: str) -> JsonResponse:
    """
    Получение информации о странах по названию.

    Сначала метод ищет данные в БД. Если данные не найдены, то делается запрос к API.
    После получения данных от API они сохраняются в БД.

    :param Request request: Объект запроса
    :param str name: Название страны
    :return:
    """

    if countries := CountryService().get_countries(name):
        serializer = CountrySerializer(countries, many=True)

        return JsonResponse(serializer.data, safe=False)

    raise NotFound


@api_view(["GET"])
def get_countries(request: Request) -> JsonResponse:
    """
    Получение информации о всех странах в базе данных.

    :param Request request: Объект запроса
    :return:
    """

    if countries := CountryService().get_all_countries():
        page = paginator.paginate_queryset(countries, request)
        serializer = CountrySerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    return JsonResponse([], safe=False)


@api_view(["GET"])
def get_weather(request: Request, alpha2code: str, city: str) -> JsonResponse:
    """
    Получение информации о погоде в указанном городе.

    :param Request request: Объект запроса
    :param str alpha2code: ISO Alpha2 код страны
    :param str city: Город
    :return:
    """

    cache_key = f"{alpha2code}_{city}"
    data = caches[CACHE_WEATHER].get(cache_key)
    if not data:
        if data := WeatherService().get_weather(alpha2code=alpha2code, city=city):
            caches[CACHE_WEATHER].set(cache_key, data)

    if data:
        serializer = WeatherSerializer(data, many=True)

        return JsonResponse(serializer.data, safe=False)

    return JsonResponse([], safe=False)


@api_view(["GET"])
def get_currency(request: Request, code: str) -> JsonResponse:
    """
    Получение информации о курсах валют для указанной валюты.

    :param Request request: Объект запроса
    :param str code: трехзначный код валюты

    :return:
    """
    data = caches[CACHE_WEATHER].get(code)
    if not data:
        if data := CurrencyService().get_currency_rates(code=code):
            caches[CACHE_WEATHER].set(code, data)

    if data:
        serializer = CurrencySerializer(data, many=True)

        return JsonResponse(serializer.data, safe=False)

    return JsonResponse([], safe=False)

from django.db.models import Q, QuerySet

from geo.clients.weather import WeatherClient
from geo.models import Weather
from geo.clients.shemas import WeatherInfoDTO


class WeatherService:
    """
    Сервис для работы с данными о погоде.
    """

    def get_weather(self, alpha2code: str, city: str) -> QuerySet[Weather]:
        """
        Получение погоды в заданном городе.

        :param alpha2code: ISO Alpha2 код страны
        :param city: Город
        :return:
        """

        weather = Weather.objects.filter(Q(country__iregex=alpha2code) | Q(city__iregex=city))

        if not weather:
            if data := WeatherClient().get_weather(f"{city},{alpha2code}"):
                self.build_model(data)
                weather = Weather.objects.filter(Q(country__iregex=alpha2code) | Q(city__iregex=city))

        return weather

    def build_model(self, weatherDTO: WeatherInfoDTO) -> Weather:
        """
        Создание модели Weather

        :param weatherDTO: DTO-модель описания погоды.
        :return:
        """

        return Weather.objects.create(
            country=weatherDTO.country,
            city=weatherDTO.city,
            temp=weatherDTO.temp,
            pressure=weatherDTO.pressure,
            humidity=weatherDTO.humidity,
            wind_speed=weatherDTO.wind_speed,
            description=weatherDTO.description,
        )
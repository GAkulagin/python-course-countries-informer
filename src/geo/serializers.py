from rest_framework import serializers

from geo.models import Country, City, Weather, CurrencyRate


class CountrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о стране.
    """

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "alpha2code",
            "alpha3code",
            "capital",
            "region",
            "subregion",
            "population",
            "latitude",
            "longitude",
            "demonym",
            "area",
            "numeric_code",
            "flag",
            "currencies",
            "languages",
        ]


class CitySerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о городе.
    """

    country = CountrySerializer(read_only=True)

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "region",
            "latitude",
            "longitude",
            "country",
        ]


class WeatherSerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о погоде.
    """

    class Meta:
        model = Weather
        fields = [
            "country",
            "city",
            "temp",
            "pressure",
            "humidity",
            "wind_speed",
            "description",
        ]


class CurrencySerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о курсе валют.
    """

    class Meta:
        model = CurrencyRate
        fields = [
            "base",
            "compared_to",
            "value",
            "date",
        ]
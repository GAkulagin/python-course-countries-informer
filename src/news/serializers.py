from rest_framework import serializers

from geo.models import Country
from news.models import News


class CountrySerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о стране.
    """
    class Meta:
        model = Country
        fields = [
            "alpha2code",
            "name",
        ]


class NewsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для данных о новостях.
    """
    country = CountrySerializer(read_only=True)

    class Meta:
        model = News
        fields = [
            "published_at",
            "title",
            "source",
            "author",
            "description",
            "url",
            "country",
        ]
        ordering = ("published_at",)

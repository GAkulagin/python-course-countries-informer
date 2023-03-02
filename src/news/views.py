"""Представления Django"""
from django.core.cache import caches
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.http import JsonResponse

from app.settings import CACHE_NEWS
from news.serializers import NewsSerializer
from news.services.news import NewsService


@api_view(["GET"])
def get_country_news(request: Request, alpha2code: str) -> JsonResponse:
    """
   Получение новостей страны.

   :param Request request: Объект запроса
   :param str alpha2code: ISO Alpha2 код страны

   :return:
   """
    news = caches[CACHE_NEWS].get(alpha2code)
    if not news:
        if news := NewsService().get_news(alpha2code):
            caches[CACHE_NEWS].set(alpha2code, news)

    if news:
        serializer = NewsSerializer(news, many=True)

        return JsonResponse(serializer.data, safe=False)

    return JsonResponse([], safe=False)

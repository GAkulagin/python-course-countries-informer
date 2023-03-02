"""Представления Django"""
from django.core.cache import caches
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.http import JsonResponse
from rest_framework.settings import api_settings

from app.settings import CACHE_NEWS
from news.serializers import NewsSerializer
from news.services.news import NewsService

default_pagination = api_settings.DEFAULT_PAGINATION_CLASS
paginator = default_pagination()


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
        page = paginator.paginate_queryset(news, request)
        serializer = NewsSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)

    return JsonResponse([], safe=False)

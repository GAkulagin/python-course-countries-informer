from django.urls import path
from news.views import get_country_news


urlpatterns = [
    path("news/<str:alpha2code>", get_country_news, name="news"),
]
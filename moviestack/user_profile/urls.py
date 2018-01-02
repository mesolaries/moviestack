from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.index, name='profile_index'),
    path('favourites/', views.favourites, name='user_favs'),
    path('watchlist/', views.watchlist, name='user_watchlist'),
    path('robots.txt/', lambda r: HttpResponse("User-agent: *\nDisallow: /favourites/\nDisallow: /watchlist/", content_type='text/plain')),
]

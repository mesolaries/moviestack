from django.urls import path, re_path
from django.http import HttpResponse
from . import views


urlpatterns = [
    path('', views.ProfileIndexView.as_view()),
    path('favourites/', views.ProfileFavouritesView.as_view()),
    path('watchlist/', views.ProfileWatchlistView.as_view()),
    path('robots.txt/', lambda r, **kwargs: HttpResponse("User-agent: *\nDisallow: /favourites/\nDisallow: /watchlist/", content_type='text/plain')),
]

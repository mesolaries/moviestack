from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.ProfileIndexView.as_view()),
    path('favourites/', views.ProfileFavouritesView.as_view()),
    path('watchlist/', views.ProfileWatchlistView.as_view()),
]

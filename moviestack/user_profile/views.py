from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.contrib.auth import logout
from django.views import View
from collections import namedtuple
from homepage.models import UserMovie
from .parsing_data import get_index_data, get_favourites_data, get_watchlist_data


# Create your views here.
class ProfileIndexView(View):
    template_name = "profile/profile_index.html"

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/')

    def get(self, request, username, *args, **kwargs):
        user = get_user_data(request, username) # Get user movies data from db
        if isinstance(user, HttpResponse):
            return user
        else:
            user_data = user.user_data
            active_user = user.active_user

            if user_data.watchlist_movies_ids == '':
                if user_data.fav_movies_ids == '':
                    fav_count = 0
                else:
                    fav_ids = user_data.fav_movies_ids_as_list()
                    fav_count = len(fav_ids)
                watchlist_count = 0
                cover = ""
                context = {
                    'username': username, 'active_user': active_user,
                    'fav_count': fav_count, 'watchlist_count': watchlist_count,
                    'cover': cover
                }
            else:
                data = get_index_data(user_data)
                # Show 5 elements per page
                paginator = Paginator(list(data), 5)
                page = request.GET.get('page')
                upcoming_data = paginator.get_page(page)

                context = {
                    'username': username, 'active_user': active_user,
                    'upcoming_data': data.upcoming_data, 'fav_count': data.fav_count,
                    'watchlist_count': data.watchlist_count,
                    'upcoming_count': data.upcoming_count, 'cover': data.cover
                }
        return render(request, self.template_name, context)


class ProfileFavouritesView(View):
    template_name = "profile/profile_favourites.html"

    def get(self, request, username, *args, **kwargs):
        user = get_user_data(request, username)
        user_data = user.user_data
        active_user = user.active_user

        if request.is_ajax():
            if user_data.fav_movies_ids == '':
                context = {}
            else:
                data = get_favourites_data(user_data)
                fav_data = data.fav_data

                paginator = Paginator(list(fav_data), 10)
                page = request.GET.get('page')
                fav_data = paginator.get_page(page)

                context = {
                    'active_user': active_user, 'user_fav_movies_id_list': data.id_list,
                    'fav_data': fav_data
                }

            html = render_to_string(self.template_name, context)
            return HttpResponse(html)
        return render(request, "profile/direct_url_error.html", {})


class ProfileWatchlistView(View):
    template_name = "profile/profile_watchlist.html"

    def get(self, request, username, *args, **kwargs):
        user = get_user_data(request, username)
        user_data = user.user_data
        active_user = user.active_user

        if request.is_ajax():
            if user_data.watchlist_movies_ids == '':
                context = {}
            else:
                data = get_watchlist_data(user_data)
                watchlist_data = data.watchlist_data

                paginator = Paginator(list(watchlist_data), 10)
                page = request.GET.get('page')
                watchlist_data = paginator.get_page(page)

                context = {
                    'active_user': active_user, 'user_watchlist_movies_id_list': data.id_list,
                    'watchlist_data': watchlist_data
                }

            html = render_to_string(self.template_name, context)
            return HttpResponse(html)
        return render(request, "profile/direct_url_error.html", {})

# Get information about current user and user movies
def get_user_data(request, username):
    list_of_users = list(User.objects.all().values_list('username', flat=True))
    try:
        active_user = User.objects.get(username=username) # Current user according to username variable from url
    except ObjectDoesNotExist:
        return render(request, "profile/direct_url_error.html")

    if str(request.user) == username:
        user_data = UserMovie.objects.get(owner=request.user)
    else:
        user_data = UserMovie.objects.get(owner=active_user)

    Point = namedtuple('Point', ['active_user', 'user_data'])
    user = Point(active_user, user_data)
    return user

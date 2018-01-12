from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
import requests
from .forms import SearchForm, SignUpForm
from .models import UserMovie
from .parsing_data import get_index_data, get_results_data, get_details_data


# Create your views here
class IndexView(View):
    form_class = SearchForm
    template_name = "homepage/index.html"

    def get(self, request, *args, **kwargs):
        if 'search' in request.GET:
            # Get search results
            search = request.GET.get("search")
            form = self.form_class(request.GET)
            if form.is_valid():
                data = get_results_data(request, search)  # Get data according to search query

                # Add or delete movie from db
                if 'movieId' in request.GET:
                    movie_id = request.GET['movieId']

                    comma_movie_id = ','+movie_id
                    movie_id_comma = movie_id+','

                    user = UserMovie.objects.get(owner=request.user)

                    if 'add-to-favs' in request.GET['type']:
                        user.add_to_favs(movie_id, comma_movie_id, movie_id_comma)

                    elif 'add-to-watchlist' in request.GET['type']:
                        user.add_to_watchlist(movie_id, comma_movie_id, movie_id_comma)

                    elif 'delete-from-favs' in request.GET['type']:
                        user.delete_from_favs(movie_id, comma_movie_id, movie_id_comma)

                    elif 'delete-from-watchlist' in request.GET['type']:
                        user.delete_from_watchlist(movie_id, comma_movie_id, movie_id_comma)

                context = {
                            'form': form,
                            'total_results': data['total_results'],
                            'zipped_id_poster_backdrop_title_vote_genres_overview_date': data['results'],
                            'page_number': data['page_number'],
                            'total_pages': data['total_pages'],
                            'range': range(1, data['total_pages']+1), 'search': search
                        }

                # Add user movies information to context if user is authenticated
                if request.user.is_authenticated:
                    user_data = UserMovie.objects.get(owner=request.user)
                    context['data_favs'] = user_data.fav_movies_ids
                    context['data_watchlist'] = user_data.watchlist_movies_ids
                return render(request, "homepage/search_results.html", context)
        else:
            # Empty form and index page
            form = self.form_class()
            data = get_index_data()

        return render(request, self.template_name, {'form': form,
                                                    'zipped_poster_title_id_first': data[0],
                                                    'zipped_poster_title_id_second': data[1]})

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/')


class DetailsView(View):
    template_name = "homepage/movie_details.html"

    def get(self, request, movie_id, *args, **kwargs):
        data = get_details_data(movie_id)  # Get movie data using movie ID

        if not data:
            return HttpResponse("No movie found")
        else:
            if 'movieId' in request.GET:
                comma_movie_id = ','+movie_id
                movie_id_comma = movie_id+','

                user_data = UserMovie.objects.get(owner=request.user)

                if 'add-to-favs' in request.GET['type']:
                    user_data.add_to_favs(movie_id, comma_movie_id, movie_id_comma)

                elif 'add-to-watchlist' in request.GET['type']:
                    user_data.add_to_watchlist(movie_id, comma_movie_id, movie_id_comma)

                elif 'delete-from-favs' in request.GET['type']:
                    user_data.delete_from_favs(movie_id, comma_movie_id, movie_id_comma)

                elif 'delete-from-watchlist' in request.GET['type']:
                    user_data.delete_from_watchlist(movie_id, comma_movie_id, movie_id_comma)

            context = {
                        "poster_img_url": data.poster, "title": data.title,
                        "overview": data.overview, "release_date": data.release_date,
                        "vote_average": data.vote_average, "videos_zip": data.videos,
                        "trailer_url": data.trailer_url, "trailer_name": data.trailer_name,
                        "status": data.status, "tagline": data.tagline,
                        "backdrop_img_url": data.backdrop, "genres": data.genres,
                        "zipped_name_char_profile": data.cast,
                        "zipped_recom_back_title_vote_id": data.recom_movies,
                        "movie_id": movie_id,
                    }
            if request.user.is_authenticated:
                user_data = UserMovie.objects.get(owner=request.user)
                context['data_favs'] = user_data.fav_movies_ids
                context['data_watchlist'] = user_data.watchlist_movies_ids
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(request.path)


class SignUpView(View):
    form_class = SignUpForm
    template_name = "registration/signup.html"

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', '/'))

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


class LogInView(View):
    template_name = "registration/login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(request.GET.get('next', '/'))
        else:
            error = "Incorrect username or password"
            context = {'error': error}
            return render(request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

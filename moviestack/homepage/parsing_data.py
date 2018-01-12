import requests
import random
from datetime import datetime
from django.http import HttpResponse
from collections import namedtuple

# Global variables
api_key = "3414ea60e31cadae72ad7fbe5cfb7482"
image_base_url = "https://image.tmdb.org/t/p/{size}{path}"
search_base_url = "https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={query}&page={number}"
search_id_base_url = "https://api.themoviedb.org/3/movie/{id}?api_key={api_key}"
search_id_credits_base_url = "https://api.themoviedb.org/3/movie/{id}/credits?api_key={api_key}"
search_id_video_base_url = "https://api.themoviedb.org/3/movie/{id}/videos?api_key={api_key}&language=en-US"
youtube_base_url = "https://youtube.com/embed/{video_key}"
now_playing_movies_base_url = "https://api.themoviedb.org/3/movie/now_playing?api_key={api_key}&page=1"
recommendations_base_url = "https://api.themoviedb.org/3/movie/{id}/recommendations?api_key={api_key}&language=en-US&page=1"

movie_genres_by_id = {
                "28": "Action", "12": "Adventure", "16": "Animation",
                "35": "Comedy", "80": "Crime", "99": "Documentary",
                "18": "Drama", "10751": "Family", "14": "Fantasy",
                "36": "History", "27": "Horror", "10402": "Music",
                "9648": "Mystery", "10749": "Romance", "878": "Science Fiction",
                "10770": "TV Movie", "53": "Thriller", "10752": "War", "37": "Western"
                }


def get_index_data():
    # GET 4 random movies
    now_playing_movies_url = now_playing_movies_base_url.format(api_key=api_key)
    data = requests.get(now_playing_movies_url).json()
    now_playing_movies = data.get('results')

    poster_img_urls = []
    titles = []
    movie_id_list = []
    for i in range(4):
        random_movie_index = random.randint(0, len(now_playing_movies)-1)
        current_movie = now_playing_movies[random_movie_index]

        path = current_movie.get("poster_path")
        poster_img_url = image_base_url.format(size='w185', path=path)

        poster_img_urls.append(poster_img_url)

        titles.append(current_movie.get("title"))
        movie_id_list.append(current_movie.get("id"))

        now_playing_movies.pop(random_movie_index)

    zipped_poster_title_id_first = zip(poster_img_urls[:2], titles[:2], movie_id_list[:2])
    zipped_poster_title_id_second = zip(poster_img_urls[2:], titles[2:], movie_id_list[2:])

    return zipped_poster_title_id_first, zipped_poster_title_id_second


def get_results_data(request, search):
    movie_id_list = []
    poster_img_urls = []
    backdrop_img_urls = []
    movie_titles = []
    movie_vote_list = []
    movie_genre_list = []
    movie_overview_list = []
    movie_release_date_list = []

    page_number = int(request.GET.get('page', 1))

    search_movies_url = search_base_url.format(api_key=api_key, query=search, number=page_number)
    search_results_data = requests.get(search_movies_url).json()  # GET DATA (using requests module) and convert them to json()
    total_results = search_results_data.get("total_results")  # Get "total_results" from data
    total_pages = search_results_data.get("total_pages", 1)
    movies = search_results_data.get("results", "")

    for movie in movies:
        poster_path = movie.get("poster_path")
        poster_img_url = image_base_url.format(size="w185", path=poster_path)
        poster_img_urls.append(poster_img_url)

        backdrop_path = movie.get("backdrop_path")
        backdrop_img_url = image_base_url.format(size="w780", path=backdrop_path)
        backdrop_img_urls.append(backdrop_img_url)

        movie_id_list.append(str(movie.get("id")))
        movie_titles.append(movie.get("title"))
        movie_vote_list.append(movie.get("vote_average"))
        movie_overview_list.append(movie.get("overview"))

        str_date = movie.get("release_date")
        if str_date == '':
            movie_release_date_list.append("")
        else:
            date_object = datetime.strptime(str_date, '%Y-%m-%d').date()
            movie_release_date_list.append(date_object)

        genre_id_list = movie.get("genre_ids")
        current_movie_genres = []
        for genre_id in genre_id_list:
            genre_name = movie_genres_by_id.get(str(genre_id))
            current_movie_genres.append(genre_name)
        movie_genre_list.append(current_movie_genres)

    zipped_id_poster_backdrop_title_vote_genres_overview_date = zip(movie_id_list, poster_img_urls, backdrop_img_urls, movie_titles, movie_vote_list, movie_genre_list, movie_overview_list, movie_release_date_list)

    return {
        'results': zipped_id_poster_backdrop_title_vote_genres_overview_date,
        'page_number': page_number, 'total_results': total_results, 'total_pages': total_pages
    }


def get_details_data(movie_id):
    get_movie_url = search_id_base_url.format(id=movie_id, api_key=api_key)
    get_credits_url = search_id_credits_base_url.format(id=movie_id, api_key=api_key)
    movie_details = requests.get(get_movie_url).json()
    movie_credits = requests.get(get_credits_url).json()

    if movie_details.get("status_code", None) == 34:
        return False
    else:
        poster_path = movie_details.get("poster_path")
        poster_img_url = image_base_url.format(size="w500", path=poster_path)
        backdrop_path = movie_details.get("backdrop_path")
        backdrop_img_url = image_base_url.format(size="w1280", path=backdrop_path)
        status = movie_details.get("status")
        vote_average = movie_details.get("vote_average")
        tagline = movie_details.get("tagline")
        title = movie_details.get("title")
        overview = movie_details.get("overview")
        genres = []
        for genre in movie_details.get("genres"):
            genres.append(genre.get("name"))

        str_date = movie_details.get("release_date")
        if str_date:
            release_date = datetime.strptime(str_date, '%Y-%m-%d').date()
        else:
            release_date = ''

        movie_cast = movie_credits.get("cast")
        name = []
        character = []
        profile_img_url = []

        actors_number_to_view = 10
        if len(movie_cast) < 10:
            actors_number_to_view = len(movie_cast)
        for i in range(actors_number_to_view):
            name.append(movie_cast[i].get("name"))
            character.append(movie_cast[i].get("character"))
            profile_path = movie_cast[i].get("profile_path")
            profile_img_url.append(image_base_url.format(size="w342", path=profile_path))

        zipped_name_char_profile = zip(name, character, profile_img_url)

        get_video_url = search_id_video_base_url.format(id=movie_id, api_key=api_key)
        videos = requests.get(get_video_url).json()
        movie_videos_list = videos['results']

        other_video_urls = []
        other_video_names = []
        trailer = {}
        trailer_key, trailer_name, trailer_url = "", "", ""
        for trailer in movie_videos_list:
            if trailer['type'] == "Trailer":
                trailer_key = trailer['key']
                trailer_name = trailer['name']
                trailer_url = youtube_base_url.format(video_key=trailer_key)
                break

        if len(movie_videos_list) != 0:
            movie_videos_list.pop(movie_videos_list.index(trailer))

        for video in movie_videos_list:
            other_video_urls.append(youtube_base_url.format(video_key=video['key']))
            other_video_names.append(video['name'])

        zipped_other_video_urls_names = zip(other_video_urls, other_video_names)

        recommendations = requests.get(recommendations_base_url.format(id=movie_id, api_key=api_key)).json()
        recom_movies = recommendations.get('results')[:5]
        recom_backdrop_img_urls = []
        recom_titles = []
        recom_vote_average_list = []
        recom_movie_id_list = []
        for recom_movie in recom_movies:
            recom_backdrop_path = recom_movie.get("backdrop_path")
            recom_backdrop_img_urls.append(image_base_url.format(size='w780', path=recom_backdrop_path))
            recom_titles.append(recom_movie.get("title"))
            recom_vote_average_list.append(recom_movie.get("vote_average"))
            recom_movie_id_list.append(recom_movie.get("id"))
        zipped_recom_back_title_vote_id = zip(recom_backdrop_img_urls, recom_titles, recom_vote_average_list, recom_movie_id_list)

        Point = namedtuple('Point', [
                                    'poster', 'title', 'overview',
                                    'release_date', 'vote_average', 'videos',
                                    'trailer_url', 'trailer_name', 'status',
                                    'tagline', 'backdrop', 'genres',
                                    'cast', 'recom_movies'
                                    ])
        data = Point(
                    poster_img_url, title, overview, release_date, vote_average,
                    zipped_other_video_urls_names, trailer_url, trailer_name, status, tagline,
                    backdrop_img_url, genres, zipped_name_char_profile,
                    zipped_recom_back_title_vote_id
                    )
        return data

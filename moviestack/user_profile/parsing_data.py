import requests
from datetime import datetime, timedelta
from collections import namedtuple

api_key = "3414ea60e31cadae72ad7fbe5cfb7482"
image_base_url = "https://image.tmdb.org/t/p/{size}{path}"
search_id_base_url = "https://api.themoviedb.org/3/movie/{id}?api_key={api_key}"


def get_index_data(user):
    # UPCOMING FROM WATCHLIST
    upcoming_titles = []
    upcoming_backdrop_img_urls = []
    upcoming_release_date_list = []
    upcoming_genres = []
    upcoming_id_list = []

    watchlist_ids = user.watchlist_movies_ids_as_list()
    fav_ids = user.fav_movies_ids_as_list()

    watchlist_count = len(watchlist_ids)
    if user.fav_movies_ids == '':
        fav_count = 0
    else:
        fav_count = len(fav_ids)

    today = datetime.now()
    one_month_later = (today + timedelta(days=30)).date()

    for watchlist_id in watchlist_ids:
        upcoming_url = search_id_base_url.format(id=watchlist_id, api_key=api_key)
        upcoming_results = requests.get(upcoming_url).json()
        str_date = upcoming_results.get("release_date", "")
        release_date = datetime.strptime(str_date, '%Y-%m-%d').date()
        if release_date <= one_month_later and release_date >= today.date():
            upcoming_release_date_list.append(release_date)
            upcoming_titles.append(upcoming_results.get("title"))
            upcoming_id_list.append(upcoming_results.get("id"))

            upcoming_path = upcoming_results.get("backdrop_path")
            upcoming_backdrop_img_urls.append(image_base_url.format(size='w780', path=upcoming_path))
            current_movie_genres = []
            for genre in upcoming_results.get("genres"):
                current_movie_genres.append(genre.get("name"))
            upcoming_genres.append(current_movie_genres)
    if len(upcoming_backdrop_img_urls) > 0:
        cover = image_base_url.format(size='original', path=upcoming_path)  # Get last added movies backdrop for site cover
    else:
        cover = ""

    upcoming_count = len(upcoming_id_list)

    zipped_upcoming_backdrop_title_genres_date = zip(upcoming_backdrop_img_urls, upcoming_titles, upcoming_genres, upcoming_release_date_list, upcoming_id_list)

    Point = namedtuple('Point', ['upcoming_data', 'cover', 'fav_count', 'watchlist_count', 'upcoming_count'])
    data = Point(
                zipped_upcoming_backdrop_title_genres_date,
                cover, fav_count, watchlist_count, upcoming_count
                )
    return data


def get_favourites_data(user):
    user_fav_movies_id_list = user.fav_movies_ids_as_list()

    fav_backdrop_img_urls = []
    fav_movie_titles = []
    fav_movie_overview_list = []
    fav_movie_release_date_list = []
    fav_movie_genre_list = []
    fav_movie_id_list = []

    for fav_id in user_fav_movies_id_list:
        get_movie_url = search_id_base_url.format(id=fav_id, api_key=api_key)
        movie = requests.get(get_movie_url).json()

        backdrop_path = movie.get("backdrop_path")
        backdrop_img_url = image_base_url.format(size="w780", path=backdrop_path)
        fav_backdrop_img_urls.append(backdrop_img_url)

        title = movie.get("title")
        fav_movie_titles.append(title)
        overview = movie.get("overview")
        fav_movie_overview_list.append(overview)

        fav_movie_id_list.append(fav_id)

        str_date = movie.get("release_date", "")
        if str_date == '' or str_date is None:
            fav_movie_release_date_list.append("")
        else:
            date_object = datetime.strptime(str_date, '%Y-%m-%d').date()
            fav_movie_release_date_list.append(date_object)

        genres = movie.get("genres", "")
        current_movie_genres = []
        for genre in genres:
            genre_name = genre.get("name")
            current_movie_genres.append(genre_name)
        fav_movie_genre_list.append(current_movie_genres)

    fav_data = zip(
                fav_backdrop_img_urls,
                fav_movie_titles, fav_movie_release_date_list,
                fav_movie_genre_list, fav_movie_overview_list,
                fav_movie_id_list
                )

    Point = namedtuple("Point", ["fav_data", "id_list"])
    data = Point(fav_data, user_fav_movies_id_list)

    return data


def get_watchlist_data(user):
    user_watchlist_movies_id_list = user.watchlist_movies_ids_as_list()

    watchlist_backdrop_img_urls = []
    watchlist_movie_titles = []
    watchlist_movie_overview_list = []
    watchlist_movie_release_date_list = []
    watchlist_movie_genre_list = []
    watchlist_movie_id_list = []

    for watchlist_id in user_watchlist_movies_id_list:
        get_movie_url = search_id_base_url.format(id=watchlist_id, api_key=api_key)
        movie = requests.get(get_movie_url).json()

        backdrop_path = movie.get("backdrop_path")
        backdrop_img_url = image_base_url.format(size="w780", path=backdrop_path)
        watchlist_backdrop_img_urls.append(backdrop_img_url)

        title = movie.get("title")
        watchlist_movie_titles.append(title)
        overview = movie.get("overview")
        watchlist_movie_overview_list.append(overview)

        watchlist_movie_id_list.append(watchlist_id)

        str_date = movie.get("release_date", "")
        if str_date == '' or str_date is None:
            watchlist_movie_release_date_list.append("")
        else:
            date_object = datetime.strptime(str_date, '%Y-%m-%d').date()
            watchlist_movie_release_date_list.append(date_object)

        genres = movie.get("genres", "")
        current_movie_genres = []
        for genre in genres:
            genre_name = genre.get("name")
            current_movie_genres.append(genre_name)
        watchlist_movie_genre_list.append(current_movie_genres)

    watchlist_data = zip(watchlist_backdrop_img_urls, watchlist_movie_titles, watchlist_movie_release_date_list, watchlist_movie_genre_list, watchlist_movie_overview_list, watchlist_movie_id_list)

    Point = namedtuple("Point", ["watchlist_data", "id_list"])
    data = Point(watchlist_data, user_watchlist_movies_id_list)

    return data

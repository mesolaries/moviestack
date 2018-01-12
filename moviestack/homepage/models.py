from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import validate_comma_separated_integer_list
import requests
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class UserMovie(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    fav_movies_ids = models.TextField(validators=[validate_comma_separated_integer_list], blank=True)
    watchlist_movies_ids = models.TextField(validators=[validate_comma_separated_integer_list], blank=True)

    def fav_movies_ids_as_list(self):
        return self.fav_movies_ids.split(',')

    def watchlist_movies_ids_as_list(self):
        return self.watchlist_movies_ids.split(',')

    def add_to_favs(self, movie_id, comma_movie_id, movie_id_comma):
        if self.fav_movies_ids == '':
            updated_id = movie_id
        else:
            updated_id = self.fav_movies_ids + comma_movie_id # Old ID string + New ID
        self.fav_movies_ids = updated_id
        return self.save()

    def add_to_watchlist(self, movie_id, comma_movie_id, movie_id_comma):
        if self.watchlist_movies_ids == '':
            updated_id = movie_id
        else:
            updated_id = self.watchlist_movies_ids + comma_movie_id
        self.watchlist_movies_ids = updated_id
        return self.save()

    def delete_from_favs(self, movie_id, comma_movie_id, movie_id_comma):
        user_fav_movies_id_list = self.fav_movies_ids_as_list()
        if movie_id in user_fav_movies_id_list[0] and len(user_fav_movies_id_list) > 1:
            updated_id = self.fav_movies_ids.replace(movie_id_comma, '')
        elif comma_movie_id in self.fav_movies_ids:
            updated_id = self.fav_movies_ids.replace(comma_movie_id, '')
        else:
            updated_id = self.fav_movies_ids.replace(movie_id, '')
        self.fav_movies_ids = updated_id
        self.save()

    def delete_from_watchlist(self, movie_id, comma_movie_id, movie_id_comma):
        user_watchlist_movies_id_list = self.watchlist_movies_ids_as_list()

        if movie_id in user_watchlist_movies_id_list[0] and len(user_watchlist_movies_id_list) > 1:
            updated_id = self.watchlist_movies_ids.replace(movie_id_comma, '')
        elif comma_movie_id in self.watchlist_movies_ids:
            updated_id = self.watchlist_movies_ids.replace(comma_movie_id, '')
        else:
            updated_id = self.watchlist_movies_ids.replace(movie_id, '')
        self.watchlist_movies_ids = updated_id
        self.save()

    def __str__(self):
        return str(self.owner)

# Automatically adding users to Owner when new user created/updated/deleted
# SOURCE: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserMovie.objects.create(owner=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.usermovie.save()

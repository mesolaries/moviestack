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

    def delete_from_favs(self, user, movie_id, comma_movie_id, movie_id_comma, data):
        user_fav_movies_id_list = user.fav_movies_ids_as_list()
        if movie_id in user_fav_movies_id_list[0] and len(user_fav_movies_id_list) > 1: # If current movie id is first in database
            updated_id = data.fav_movies_ids.replace(movie_id_comma, '')
        elif comma_movie_id in data.fav_movies_ids:
            updated_id = data.fav_movies_ids.replace(comma_movie_id, '')
        else:
            updated_id = data.fav_movies_ids.replace(movie_id, '')
        data.fav_movies_ids = updated_id # Update field
        data.save() # save changes

    def delete_from_watchlist(self, user, movie_id, comma_movie_id, movie_id_comma, data):
        user_watchlist_movies_id_list = user.watchlist_movies_ids_as_list()
        if movie_id in user_watchlist_movies_id_list[0] and len(user_watchlist_movies_id_list) > 1: # If current movie id is first in database
            updated_id = data.watchlist_movies_ids.replace(movie_id_comma, '')
        elif comma_movie_id in data.watchlist_movies_ids:
            updated_id = data.watchlist_movies_ids.replace(comma_movie_id, '')
        else:
            updated_id = data.watchlist_movies_ids.replace(movie_id, '')
        data.watchlist_movies_ids = updated_id # Update field
        data.save() # save changes

    def __str__(self):
        return str(self.owner)

# class Comment(models.Model):
#     owner = models.ForeignKey(User, on_delete=models.CASCADE)
#     on_movie = models.IntegerField(blank=True)
#     comment = models.TextField(blank=True)
#
#     def __str__(self):
#         return str(self.comment)

# Automatically adding users to Owner when new user created/updated/deleted
# SOURCE: https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserMovie.objects.create(owner=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.usermovie.save()

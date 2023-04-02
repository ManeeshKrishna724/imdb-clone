from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Watchlist(models.Model):
    profile = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    movie_show = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    added_date = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.movie_show + self.year
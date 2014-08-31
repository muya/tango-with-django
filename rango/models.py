from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(max_length=11, default=0)
    likes = models.IntegerField(max_length=11, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title


class UserProfile(models.Model):
    # links UserProfile to a User model instance
    user = models.OneToOneField(User)

    # the additional attributes
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __unicode__(self):
        return self.user.username

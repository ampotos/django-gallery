import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit_selectize.managers import TaggableManager
from django.conf import settings

# Create your models here.

class Listing(models.Model):
    description = models.CharField(max_length=500, blank=True)
    name = models.CharField(max_length=100, blank=False)
    link = models.URLField(max_length=500, unique=True, blank=True)
    # tags mechanism
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name_plural = "Listings"
        permissions = (("can_tag", "Allow normal user to tag listing"),)

    def __str__(self):
        return self.link + '(' + self.description + ')'

    def get_absolute_url(self):
        return reverse(
            "listing:single",
            kwargs={"pk": self.pk},
        )

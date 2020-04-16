import random
import shutil # for filesystem cleanup
from os.path import isdir # to check if directory exists
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit_selectize.managers import TaggableManager


# Create your models here.

class Picture(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    picture = models.ImageField(upload_to="", default="blank/no_img.png")
    description = models.CharField(max_length=500, default="Empty", unique=True)
    name = models.CharField(max_length=200)
    # tags mechanism
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name_plural = "Pictures"
        ordering = ("-pk",)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse(
            "gallery:single_picture",
            kwargs={"pk": self.pk},
        )

    def delete(self, *args, **kwargs):
        """Custom delete method to remove pictures references not only from db, 
        but also from the filesystem"""
        self.picture.delete()
        super().delete(*args, **kwargs)

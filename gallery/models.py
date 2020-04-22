import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit_selectize.managers import TaggableManager
from django.conf import settings

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
        permissions = (("can_tag", "Allow normal user to tag pictures"),)   

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
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.picture.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, self.picture.name))
        self.picture.delete()
        super().delete(*args, **kwargs)

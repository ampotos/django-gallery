import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from taggit_selectize.managers import TaggableManager
from django.conf import settings

# Create your models here.

class Model3D(models.Model):
    creation_date = models.DateTimeField(default=timezone.now)
    search_img = models.ForeignKey('Image', on_delete=models.DO_NOTHING, related_name='search_img', null=True)
    description = models.CharField(max_length=500, default="Empty", unique=True)
    name = models.CharField(max_length=200)
    # tags mechanism
    tags = TaggableManager(blank=True)

    class Meta:
        verbose_name_plural = "3DModels"
        ordering = ("-pk",)
        permissions = (("can_tag", "Allow normal user to tag model"),)   

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse(
            "gallery:single_model",
            kwargs={"pk": self.pk},
        )

    def delete(self, *args, **kwargs):
        """Custom delete method to all images of this model"""
        self.search_img = None
        self.save()
        for i in Image.objects.filter(linked_model=self.pk):
            i.delete()
        super().delete(*args, **kwargs)

class Image(models.Model):
    img = models.ImageField(upload_to="", default="blank/no_img.png")
    linked_model = models.ForeignKey('Model3D', on_delete=models.DO_NOTHING, related_name='model')

    class Meta:
        managed = True
    
    def delete(self, *args, **kwargs):
        """Custom delete method to remove image references not only from db, 
        but also from the filesystem"""
        if self.linked_model.search_img.pk == self.pk:
            self.linked_model.search_img = None
            self.linked_model.save()
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.img.name)):
            os.remove(os.path.join(settings.MEDIA_ROOT, self.img.name))
        self.img.delete()
        super().delete(*args, **kwargs)

    

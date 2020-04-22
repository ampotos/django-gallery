from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, permission_required
from django.db.models import Q  # complex lookups (for searching)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.views.generic.list import ListView
from django.core.files.images import ImageFile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Picture
from .forms import UploadZipForm
from taggit.models import Tag
from random import randint
from zipfile import ZipFile, BadZipFile
from PIL import Image
from io import BytesIO
import json
import uuid

class IsSuperuserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# Create your views here.
class ZipUpload(IsSuperuserMixin, FormView):
    form_class = UploadZipForm
    template_name = "gallery/upload_zip.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form, 'upload_state': self.kwargs.get("upload_state", None)})
    
    def process_zip(self, zipfile):
        try:
            with ZipFile(zipfile) as z:
                if 'config.json' not in z.namelist():
                    return 'no config.json'
                try:
                    config = json.load(z.open('config.json'))
                except json.JSONDecodeError as e:
                    return 'json error: ' + e.what()
                
                for img in config:
                    # to avoid null tags
                    if img['tags'].endswith(','):
                        img['tags'] = img['tags'][:-1]
                        
                    if img['stl_path'] == "":
                        return 'missing stl_path'

                    if img['img_name'] == "":
                        for picture in Picture.objects.filter(description=img['stl_path']):
                            picture.tags.add(*img['tags'].split(','))
                            picture.save()
                        continue
                    else:
                        # get image data 
                        img_name = ".".join(img['img_name'].split('.')[:-1])
                        random_name = '%s%s.%s' % (img_name, uuid.uuid4(), img['img_name'].split('.')[-1])
                        random_path = '%s/%s' % (settings.MEDIA_ROOT, random_name)
                        img_data = z.read(img['img_name'])
                        

                    if Picture.objects.filter(description=img['stl_path']).count() != 0:
                        # we already have that in db let's update tag and image if present
                        for picture in Picture.objects.filter(description=img['stl_path']):
                            picture.tags.add(*img['tags'].split(','))
                            picture.save()

                            if img['img_name'] != "":
                                picture.picture.delete()
                                picture.picture.save(random_name, BytesIO(img_data), save=True)
                                picture.name = img['img_name']
                                picture.save()
                            
                        continue
                    
                    try:
                        new_pic = Picture(
                            description = img['stl_path'],
                            name = img_name,
                        )
                        new_pic.save()
                        new_pic.picture.save(random_name, BytesIO(img_data), save=True)
                        new_pic.tags.add(*img['tags'].split(','))
                        new_pic.save()
                    except Exception as e:
                        return 'cannot save new picture: ' + e.what()
        except BadZipFile:
            return 'not a valid zip'
        return 'Success'
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            return redirect('gallery:upload', upload_state=self.process_zip(request.FILES['file']))

        return render(request, self.template_name, {"form": form})
    
class PictureMenu(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "gallery/home.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = list(filter(lambda x: x['img'], [{'name': t.name, 'img': self.get_random_img_tag(t)} for t in Tag.objects.all()]))
        return context

    def get_random_img(self):
        pictures =  Picture.objects.all()
        if len(pictures):
            return pictures[randint(0, len(pictures) - 1)]
        return 0
        
    def get_random_img_tag(self, tag):
        tagged_img = list(Picture.objects.filter(tags__name__in=[tag.name]))
        if len(tagged_img):
            return tagged_img[randint(0, len(tagged_img) - 1)]
        return None

class PictureAll(LoginRequiredMixin, ListView):
    model = Picture
    template_name = "gallery/pictures_all.html"
    context_object_name = "pictures"
    ordering = ("-creation_date",)
    paginate_by = 50

class PictureUpdate(IsSuperuserMixin, UpdateView):
    model = Picture
    fields = ['description', 'tags']
    template_name = "gallery/update_picture_form.html"

    def get_success_url(self):
        return reverse_lazy('gallery:single_picture', kwargs={'pk': self.kwargs['pk']})

class PictureUpdateTagsView(PermissionRequiredMixin, UpdateView):
    model = Picture
    fields = ['tags']
    template_name = "gallery/update_picture_form.html"
    permission_required = "gallery.can_tag"

    def get_success_url(self):
        return reverse_lazy('gallery:single_picture', kwargs={'pk': self.kwargs['pk']})

class PictureSearch(LoginRequiredMixin, ListView):
    model = Picture
    context_object_name = "pictures"
    template_name = "gallery/search_pictures.html"
    paginate_by = 50
    ordering = ("-creation_date",)

    def get_queryset(self):
        # the search plit the req in multiple token
        # for each token it get all img with tag or where token is part of the name
        # results are images present in all tokens results 
        search_query = self.request.GET.get("q", None)
        if search_query:
            token = list(filter(lambda x: x != "" and not x.startswith("!"), search_query.split(" ")))
            neg_token = list(filter(lambda x: x != "" and x.startswith("!"), search_query.split(" ")))
            if not len(token):
                return []
            res = list(set(list(Picture.objects.filter(tags__name=token[0]).distinct()) + list(Picture.objects.filter(Q(name__icontains=token[0])).distinct())))
            # for each img check that neg token is not a flag and not in name
            p_to_del = []
            for p in res:
                for t in neg_token:
                    if t[1:].lower() in p.name.lower():
                        p_to_del.append(p)
                    elif p.tags.filter(Q(name=t[1:])):
                        p_to_del.append(p)

            for p in p_to_del:
                res.remove(p)
                
            for t in token[1:]:
                token_res = list(Picture.objects.filter(tags__name=t).distinct()) + list(Picture.objects.filter(Q(name__icontains=t)).distinct())
                res = list(filter(lambda x: x in token_res, res))
            return res
        
        return []


class PicturesByTags(LoginRequiredMixin, ListView):
    model = Picture
    context_object_name = "pictures"
    template_name = "gallery/pictures_by_tags.html"
    paginate_by = 50
    ordering = ("-creation_date",)

    def get_queryset(self):
        tag = self.kwargs.get("tag_name", None)
        results = []
        if tag:
            results = Picture.objects.filter(tags__name=tag)
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_name"] = self.kwargs.get("tag_name", None)
        return context


class PictureDetails(LoginRequiredMixin, DetailView):
    model = Picture
    template_name = "gallery/single_picture.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk", None)
        return context

class PictureDelete(IsSuperuserMixin, DeleteView):
    model = Picture
    success_url = reverse_lazy("gallery:pictures")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk", None)
        return context

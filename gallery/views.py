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
from .models import Model3D, Image
from .forms import UploadZipForm
from taggit.models import Tag
from random import randint
from zipfile import ZipFile, BadZipFile
from io import BytesIO
import json
import uuid
import os

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
                
                for model in config:
                    # to avoid null tags
                    if model['tags'].endswith(','):
                        model['tags'] = model['tags'][:-1]
                        
                    if model['stl_path'] == "":
                        return 'missing stl_path'

                    img_list = []
                    if len(model['img_names']) == 0:
                        for m in Model3D.objects.filter(description=model['stl_path']):
                            m.tags.add(*model['tags'].split(','))
                            m.save()
                        continue
                    else:
                        # get image data
                        for img_name in model['img_names']:
                            model_name = ".".join(img_name.split('.')[:-1])
                            random_name = '%s%s.%s' % (model_name, uuid.uuid4(), img_name.split('.')[-1])
                            random_path = '%s/%s' % (settings.MEDIA_ROOT, random_name)
                            img_data = z.read(img_name)

                            img_list.append([random_name, img_data])

                    if Model3D.objects.filter(description=model['stl_path']).count() != 0:
                        # we already have that in db let's update tag and image if present
                        for m in Model3D.objects.filter(description=model['stl_path']):
                            m.tags.add(*model['tags'].split(','))
                            m.save()

                            search_set = False
                            # todo save images here
                            for img_name, img_data in img_list:
                                img = Image(linked_model=m)
                                img.img.save(random_name, BytesIO(img_data), save=True)
                                if not search_set:
                                    m.search_img = img
                                    m.save()
                                    search_set = True
                                    
                            m.name = model_name
                            m.save()
                            
                        continue
                    
                    try:
                        new_model = Model3D(
                            description = model['stl_path'],
                            name = os.path.basename(model['stl_path'])[:-4],
                        )
                        new_model.save()
                        new_model.tags.add(*model['tags'].split(','))
                        new_model.save()
                        search_set = False
                        # todo save images here
                        for img_name, img_data in img_list:
                            img = Image(linked_model=new_model)
                            img.img.save(random_name, BytesIO(img_data), save=True)
                            if not search_set:
                                new_model.search_img = img
                                new_model.save()
                                search_set = True
                    except Exception as e:
                        return 'cannot save new model'
        except BadZipFile:
            return 'not a valid zip'
        return 'Success'
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            return redirect('gallery:upload', upload_state=self.process_zip(request.FILES['file']))

        return render(request, self.template_name, {"form": form})
    
class ModelMenu(LoginRequiredMixin, ListView):
    model = Tag
    template_name = "gallery/home.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = list(filter(lambda x: x['model'], [{'name': t.name, 'model': self.get_random_model_tag(t)} for t in Tag.objects.all()]))
        return context

    def get_model(self):
        models = Model3D.objects.all()
        return models[0]
        
    def get_random_model_tag(self, tag):
        tagged_model = list(Model3D.objects.filter(tags__name__in=[tag.name]))
        if len(tagged_model):
            return tagged_model[randint(0, len(tagged_model) - 1)]
        return None

class ModelAll(LoginRequiredMixin, ListView):
    model = Model3D
    template_name = "gallery/models_all.html"
    context_object_name = "models"
    ordering = ("-creation_date",)
    paginate_by = 50

class ModelUpdate(IsSuperuserMixin, UpdateView):
    model = Model3D
    fields = ['description', 'tags', 'search_img']
    template_name = "gallery/update_model_form.html"

    def get_form(self, form_class=None):    
        form = super().get_form(form_class)
        form.fields["search_img"].queryset = Image.objects.filter(linked_model=self.kwargs.get("pk", None))
        return form
    
    def get_all_img(self):
        return Image.objects.filter(linked_model=self.kwargs.get("pk", None))
        
    def get_success_url(self):
        return reverse_lazy('gallery:single_model', kwargs={'pk': self.kwargs['pk']})

class ModelUpdateTagsView(PermissionRequiredMixin, UpdateView):
    model = Model3D
    fields = ['tags']
    template_name = "gallery/update_model_form.html"
    permission_required = "gallery.can_tag"

    def get_success_url(self):
        return reverse_lazy('gallery:single_model', kwargs={'pk': self.kwargs['pk']})

class ModelSearch(LoginRequiredMixin, ListView):
    model = Model3D
    context_object_name = "models"
    template_name = "gallery/search_models.html"
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
            res = list(set(list(Model3D.objects.filter(tags__name=token[0]).distinct()) + list(Model3D.objects.filter(Q(name__icontains=token[0])).distinct())))
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
                token_res = list(Model3D.objects.filter(tags__name=t).distinct()) + list(Model3D.objects.filter(Q(name__icontains=t)).distinct())
                res = list(filter(lambda x: x in token_res, res))
            return res
        
        return []


class ModelsByTags(LoginRequiredMixin, ListView):
    model = Model3D
    context_object_name = "models"
    template_name = "gallery/models_by_tags.html"
    paginate_by = 50
    ordering = ("-creation_date",)

    def get_queryset(self):
        tag = self.kwargs.get("tag_name", None)
        results = []
        if tag:
            results = Model3D.objects.filter(tags__name=tag)
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_name"] = self.kwargs.get("tag_name", None)
        return context


class ModelDetails(LoginRequiredMixin, DetailView):
    model = Model3D
    template_name = "gallery/single_model.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_all_img(self):
        return Image.objects.filter(linked_model=self.kwargs.get("pk", None))

class ModelDelete(IsSuperuserMixin, DeleteView):
    model = Model3D
    success_url = reverse_lazy("gallery:models")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk", None)
        return context

class ImageDelete(IsSuperuserMixin, DeleteView):
    model = Image

    def get_success_url(self):
        return reverse_lazy("gallery:single_model", kwargs={'pk': self.kwargs["model_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_pk"] = self.kwargs.get("model_pk", None)
        return context

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
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
from .models import Listing
from .forms import ListingForm
from taggit.models import Tag

class IsSuperuserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class ListingAll(LoginRequiredMixin, ListView):
    model = Listing
    template_name = "listing/listing_all.html"
    context_object_name = "listings"
    paginate_by = 50

class ListingUpdate(IsSuperuserMixin, UpdateView):
    model = Listing
    fields = ['link', 'description', 'tags', 'name']
    template_name = "listing/listing_form.html"
 
    def get_success_url(self):
        return reverse_lazy('listing:single', kwargs={'pk': self.kwargs['pk']})

class ListingUpdateTagsView(PermissionRequiredMixin, UpdateView):
    model = Listing
    fields = ['tags']
    template_name = "listing/listing_form.html"
    permission_required = "listing.can_tag"

    def get_success_url(self):
        return reverse_lazy('listing:single', kwargs={'pk': self.kwargs['pk']})

class ListingSearch(LoginRequiredMixin, ListView):
    model = Listing
    context_object_name = "listings"
    template_name = "listing/search_listing.html"
    paginate_by = 50

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
            res = list(Listing.objects.filter(tags__name=token[0]).distinct()) + list(Listing.objects.filter(Q(link__icontains=token[0])).distinct())
            # for each img check that neg token is not a flag and not in name
            l_to_del = []
            for l in res:
                for t in neg_token:
                    if t[1:].lower() in l.name.lower():
                        l_to_del.append(l)
                    elif l.tags.filter(Q(name=t[1:])):
                        l_to_del.append(l)

            for l in l_to_del:
                res.remove(l)
                
            for t in token[1:]:
                token_res = list(Listing.objects.filter(tags__name=t).distinct()) + list(Listing.objects.filter(Q(name__icontains=t)).distinct())
                res = list(filter(lambda x: x in token_res, res))
            return res
        
        return []


class ListingByTags(LoginRequiredMixin, ListView):
    model = Listing
    context_object_name = "listings"
    template_name = "listing/listing_by_tags.html"
    paginate_by = 50

    def get_queryset(self):
        tag = self.kwargs.get("tag_name", None)
        results = []
        if tag:
            results = Listing.objects.filter(tags__name=tag)
        return results
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_name"] = self.kwargs.get("tag_name", None)
        return context


class ListingDetails(LoginRequiredMixin, DetailView):
    model = Listing
    template_name = "listing/single_listing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk", None)
        return context

class ListingDelete(IsSuperuserMixin, DeleteView):
    model = Listing
    success_url = reverse_lazy("listing:all")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk", None)
        return context

class ListingAdd(IsSuperuserMixin, CreateView):
    model = Listing
    template_name = "listing/listing_form.html"
    fields = ['link', 'description', 'tags', 'name']
    
    def get_success_url(self):
        return reverse_lazy('listing:all')

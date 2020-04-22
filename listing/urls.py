from django.urls import path
from .views import *

app_name = "listing"

urlpatterns = [
    path("all/", ListingAll.as_view(), name="all"),
    path("search/", ListingSearch.as_view(), name="search"),
    path("tags/<str:tag_name>/", ListingByTags.as_view(), name="tag_name"),
    path("add/", ListingAdd.as_view(), name="add"),
    path(
        "<int:pk>/",
        ListingDetails.as_view(),
        name="single",
    ),
    path(
        "<int:pk>/delete/",
        ListingDelete.as_view(),
        name="delete",
    ),
    path(
        "<int:pk>/update/",
        ListingUpdate.as_view(),
        name="update",
    ),
    # update single picture tags only
    path(
        "<int:pk>/update_tag/",
        ListingUpdateTagsView.as_view(),
        name="update_tag",
    ),
]

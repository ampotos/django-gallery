from django.urls import path
from .views import *

app_name = "gallery"

urlpatterns = [
    # need to move to list of view by tags
    path("", PictureMenu.as_view(), name="home"),
    # need to search in name + tags
    path("search/", PictureSearch.as_view(), name="search"),
    # will be merged with search
    path("tags/<str:tag_name>/", PicturesByTags.as_view(), name="tag_name"),
    # all images
    path("image/", PictureAll.as_view(), name="pictures"),
    # upload new zip
    path("upload/zip/<str:upload_state>/", ZipUpload.as_view(), name="upload"),
    path("upload/zip/", ZipUpload.as_view(), name="upload"),
    # single picture
    path(
        "image/<int:pk>/",
        PictureDetails.as_view(),
        name="single_picture",
    ),
    # delete single picture
    path(
        "image/<int:pk>/delete/",
        PictureDelete.as_view(),
        name="delete_picture",
    ),
    # update single picture
    path(
        "image/<int:pk>/update/",
        PictureUpdate.as_view(),
        name="update_picture",
    ),
]

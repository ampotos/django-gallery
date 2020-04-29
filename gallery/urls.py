from django.urls import path
from .views import *

app_name = "gallery"

urlpatterns = [
    # need to move to list of view by tags
    path("", ModelMenu.as_view(), name="home"),
    # need to search in name + tags
    path("search/", ModelSearch.as_view(), name="search"),
    # will be merged with search
    path("tags/<str:tag_name>/", ModelsByTags.as_view(), name="tag_name"),
    # all images
    path("model/", ModelAll.as_view(), name="models"),
    # upload new zip
    path("upload/zip/<str:upload_state>/", ZipUpload.as_view(), name="upload"),
    path("upload/zip/", ZipUpload.as_view(), name="upload"),
    # single model
    path(
        "model/<int:pk>/",
        ModelDetails.as_view(),
        name="single_model",
    ),
    # delete single model
    path(
        "model/<int:pk>/delete/",
        ModelDelete.as_view(),
        name="delete_model",
    ),
    #delete single image
    path(
        "model/<int:model_pk>/img/<int:pk>/delete/",
        ImageDelete.as_view(),
        name="delete_image",
    ),
    # update single model
    path(
        "model/<int:pk>/update/",
        ModelUpdate.as_view(),
        name="update_model",
    ),
    # update single model tags only
    path(
        "model/<int:pk>/update_tag/",
        ModelUpdateTagsView.as_view(),
        name="update_model_tag",
    ),
]

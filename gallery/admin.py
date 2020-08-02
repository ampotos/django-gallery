from django.contrib import admin

from .models import Model3D, Image

from django.contrib import admin    

class Model3DAdmin(admin.ModelAdmin):
    model = Model3D
    actions = ['delete_model']

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()

    def delete_model(self, request, obj):
        obj.delete()


# Register your models here.
admin.site.register(Model3D, Model3DAdmin)
admin.site.register(Image)

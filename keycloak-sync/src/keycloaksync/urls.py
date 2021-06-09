from django.urls import path

from . import views

app_name = 'keycloaksync'

urlpatterns = [
    path(
        'synchronize_all',
        views.synchronize_all,
        name='synchronize_all'
    )
]

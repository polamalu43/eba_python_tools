from django.urls import path
from . import views
from .views.test import Test

urlpatterns = [
    path("test/", Test.as_view(), name="index"),
]

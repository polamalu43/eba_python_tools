from django.urls import path
from . import views
from .views.test_view import TestView
from .views.negative_word_check_view import NegativeWordCheckView

urlpatterns = [
    path("test/", TestView.as_view(), name="index"),
    path("nword/", NegativeWordCheckView.as_view(), name="index"),
]

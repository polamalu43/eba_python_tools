from django.urls import path
from . import views
from .views.negative_word_check_view import NegativeWordCheckView

urlpatterns = [
    path("nword/", NegativeWordCheckView.as_view(), name="index"),
]

# for the urls related to the courses app

from django.contrib import admin
from django.urls import path
from . import views # to access the views methods from the views.py file under courses


urlpatterns = [
    path("", views.courses), # to go to courses page with /courses in the url
    path("list", views.coursesList),
]
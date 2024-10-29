# for the urls related to the pages app

from django.contrib import admin
from django.urls import path
from . import views # to access the views methods from the views.py file under courses


urlpatterns = [
    path("", views.home), # to go to home screen as default
    path("home", views.home), # to go to home screen with /home in the url
    path("contact-us", views.contactUs),
    path("about-us", views.aboutUs),
]
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def home(request): # to return Home text as a response, takes request object as parameter
    return HttpResponse("Home")

def contactUs(request):
    return HttpResponse("Contact Us")

def aboutUs(request):
    return HttpResponse("About us")
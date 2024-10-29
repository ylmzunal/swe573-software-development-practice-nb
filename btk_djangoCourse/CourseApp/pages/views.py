from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def home(request): # to return Home text as a response, takes request object as parameter
    #return HttpResponse("Home")
    return render(request, "pages/home.html") 

def contactUs(request):
    #return HttpResponse("Contact Us")
    return render(request, "pages/contact.html")

def aboutUs(request):
    #return HttpResponse("About us")
    return render(request, "pages/about.html")
# to add the view methods for each url response

from django.shortcuts import render

from django.http import HttpResponse # to be able to use HttpResponse method

def courses(request): # to return Courses text as a response, takes request object as parameter
    return HttpResponse("Courses")

def coursesList(request):
    return HttpResponse("Courses List")

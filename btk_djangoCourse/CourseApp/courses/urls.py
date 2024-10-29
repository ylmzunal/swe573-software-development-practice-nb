# for the urls related to the courses app

from django.contrib import admin
from django.urls import path
from . import views # to access the views methods from the views.py file under courses


urlpatterns = [
    path("", views.coursesHome), # to go to courses page with /courses in the url
    path("list", views.courses),
    path("<course_name>", views.courseDetails),
    path("categories/<int:category_id>", views.getCoursesByCategoryId), #  using dynamic urls for various category ids and corresponding urls.
    path("categories/<str:category_name>", views.getCoursesByCategoryName, name="courses_by_category_name"), #  using dynamic urls for various category names and corresponding urls. str should be below of int as all int values are parsed from the str.
    
]
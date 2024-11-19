# to add the view methods for each url response

from datetime import date
from django.shortcuts import get_object_or_404, redirect, render

from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect # to be able to use HttpResponse method

from django.urls import reverse # to access paths dynamically

from .models import Course # to be able to use the Course model
from .models import Category # to be able to use the Category model

# for now, it is written here. later, it will be brought from the db
data = {"programming": "Programming Course",
        "mobile-programming": "Mobile Programming Course",
        "web-programming": "Web Programming Course"}


db = {
    "courses": [
        {
            "title": "Python Course" ,
            "description": "Python course description",
            "imageUrl": "Python-logo.png",
            "slug": "python-course", # url
            "date": date(2022,10,10),
            "isActive": True,
            "isUpdated": True,
        },
        {
            "title": "Django Course" ,
            "description": "Django course description",
            "imageUrl": "Django-logo.png",
            "slug": "django-course", # url
            "date": date(2024,10,10),
            "isActive": False,
            "isUpdated": True,
        },
                {
            "title": "Unity Course" ,
            "description": "Unity course description",
            "imageUrl": "Unity-logo.png",
            "slug": "unity-course", # url
            "date": date(2023,10,10),
            "isActive": True,
            "isUpdated": False,
        },
    ],
    "categories": [
        {"id": 1,
         "name": "Programming",
          "slug": "programming",
        },
        {"id": 2,
         "name": "Web development",
         "slug": "web-development",
        },
        {"id": 3,
         "name": "Game programming",
          "slug": "game-programming",
        },
    ]
}



def coursesHome(request): # to return Courses text as a response, takes request object as parameter
    #courses = db["courses"]
    #categories = db["categories"]
    courses = Course.objects.all() # to get all courses from the db
    categories = Category.objects.all() # to get all categories from the db
    # courses = Course.objects.filter(isActive=True) # to get all active courses from the db


    '''
    the active courses can be send either by sending all and checking on the html page or filtering them here as follows:
    courses =[]
    for course in courses:
        if course["isActive"] == True:
            courses.append(course)

    or using list comprehension as follows:
    courses = [course for course in db["courses"] if course["isActive"] == True]
    '''

    return render(request, "courses/coursesHome.html", {"categories": categories, "courses": courses, })


def courseDetails(request, course_id): # to return Courses text as a response, takes request object as parameter
    '''text = ""
    if course_name == "django":
        text = "Django" 
    elif course_name == "python":
        text = "Python"
    else:
        return HttpResponse("Course name is not valid.")'''
    #try:
    #    course = Course.objects.get(pk=course_id) # to get the course details from the db
    #except:
    #    raise Http404("Course not found") # to return a 404 error if the course is not found
    #above or
    course = get_object_or_404(Course, pk=course_id) # to return a 404 error if the course is not found 
    context = {"course": course} # to get the course details from the db
    return render(request, "courses/courseDetails.html", context) # to return the course details page
    #return HttpResponse(f"{text} Course Details")



def getCoursesByCategoryName(request, category_name): # a parameter for the defined variable in the urls.py should be added to dynamically go to the url. db is used to get the content
    try:
        # Get all categories and the specific category based on slug
        categories = db["categories"]
        category = next((cat for cat in categories if cat["slug"] == category_name), None)

        if not category:
            return HttpResponseNotFound("Category name is not valid.")

        # Filter courses by category
        courses = [course for course in db["courses"] if category["name"] in course["title"]]

        return render(request, "courses/categories.html", {
            "categories": categories,
            "category": category["name"],
            "category_text": f"Courses for {category['name']}",
            "courses": courses,
        })
    except:
        return HttpResponseNotFound("Category name is not valid.")

def getCoursesByCategoryId(request, category_id):
    try:
        # Find the category by ID
        category = next((cat for cat in db["categories"] if cat["id"] == category_id), None)

        if not category:
            return HttpResponseNotFound("Category ID is not valid.")

        # Redirect to the URL for the category name view
        redirect_url = reverse("courses_by_category_name", args=[category["slug"]])
        return redirect(redirect_url)
    except:
        return HttpResponseNotFound("Category ID is not valid.")
    

'''
old version using data

def coursesHome(request): # to return Courses text as a response, takes request object as parameter
    list_items = ""
    category_list = list(data.keys())
    for category_name in category_list:
        redirect_url = reverse("courses_by_category_name", args= [category_name]) # for every list item, a url is created
        list_items  += f"<li><a href= '{redirect_url}'>{category_name}</a></li>" # a html list items are created with references to the corresponding urls

    html = f"<h1>Courses</h1><br><ul>{list_items}</ul>"


    return HttpResponse(html)

def getCoursesByCategoryName(request, category_name): # a parameter for the defined variable in the urls.py should be added to dynamically go to the url. db is used to get the content
    try:
        category_list = list(data.keys())
        category_text = data[category_name] 
        courses = db["courses"]
        categories = db["categories"]

        #return HttpResponse(category_text)
        return render(request, "courses/categories.html", {"categories": categories, "category": category_name, "category_text": category_text,}) # returning an object (data between the {}) to be rendered in the courses.html
    except:
        return HttpResponseNotFound("Category name is not valid.")
    
def getCoursesByCategoryId(request, category_id): # a parameter for the defined variable in the urls.py should be added to dynamically go to the url
    category_list = list(data.keys())
    if category_id > len(category_list):
        return HttpResponseNotFound("Category ID is not valid.")
    else:
        category_name = category_list[category_id -1]
        # to get the url statically
        #return HttpResponseRedirect("/courses/category/" + category_name) # can be used as well
        #return redirect("/courses/category/" + category_name)

        # to get the url dynamically from path
        redirect_url = reverse("courses_by_category_name", args= [category_name]) # args is for the variables in the original path
        return redirect(redirect_url)
'''


'''
# a way without db
def getCoursesByCategoryName(request, category_name): # a parameter for the defined variable in the urls.py should be added to dynamically go to the url
    text = ""
    if category_name == "programming":
        text = "Programming" 
    elif category_name == "mobile-programming":
        text = "Mobile Programming"
    else:
        return HttpResponse("Category name is not valid.")
    return HttpResponse(f"{text} Courses")

# or this can be done
def getCoursesByCategory(request, category):
    text_list = category.split("-")
    text = " ".join([str(item).capitalize() for item in text_list])
    if text != "": # or a list of categories can be controlled here
        return HttpResponse(f"{text} Courses")
    else:
        return HttpResponse("Category name is not valid.")
'''



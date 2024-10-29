# to add the view methods for each url response

from django.shortcuts import redirect, render

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect # to be able to use HttpResponse method

from django.urls import reverse # to access paths dynamically

# for now, it is written here. later, it will be brought from the db
data = {"programming": "Programming Course",
        "mobile-programming": "Mobile Programming Course",
        "web-programming": "Web Programming Course"}


def courses(request): # to return Courses text as a response, takes request object as parameter
    return HttpResponse("Courses")

def coursesList(request):
    return HttpResponse("Courses List")

def courseDetails(request, course_name):
    text = ""
    if course_name == "django":
        text = "Django" 
    elif course_name == "python":
        text = "Python"
    else:
        return HttpResponse("Course name is not valid.")
    return HttpResponse(f"{text} Course Details")



def getCoursesByCategoryName(request, category_name): # a parameter for the defined variable in the urls.py should be added to dynamically go to the url. db is used to get the content
    try:
        category_text = data[category_name] 
        return HttpResponse(category_text)
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



from django.db import models

class Course(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    instructor = models.CharField(max_length=50)
    imageUrl = models.CharField(max_length=50, blank=False)
    date = models.DateField()
    isActive = models.BooleanField(default=True)

    def __str__(self): # This is a method that returns the title of the course when the db is queried
        return f"{self.title} - {self.date}"
    

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name
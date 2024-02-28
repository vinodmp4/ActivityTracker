from django.db import models


class certificate_type(models.Model):
    category = models.CharField(max_length=50,default="Untitled Category") # example National Initiative
    identifier = models.IntegerField(default=-1) # example 1, 2, 3, 4 (this is how connected certificates are identified)
    title = models.CharField(max_length=50,default="Untitled Certificate") # example NSS/ NCC
    grade = models.CharField(max_length=50,default="F") # example A, B, C, NA, Participation, First, Second, Third etc...
    score = models.IntegerField(default=0) # example 60
    year_max = models.IntegerField(default=0) # example 2

    def __str__(self):
        return "%s - %s: %s" % (self.category, self.title, self.grade)
    

class certificate(models.Model):
    owner_id = models.IntegerField(default=-1)
    doc_id = models.IntegerField(default=-1)
    doc_desc = models.CharField(max_length=150,default="Untitled Certificate")
    semester = models.IntegerField(default=-1)
    year = models.IntegerField(default=1990)
    hardcopy = models.BooleanField(default=False)
    doc_loc = models.CharField(max_length=150,default="/")
    verified = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    def __str__(self):
        return self.doc_desc


# Create your models here.

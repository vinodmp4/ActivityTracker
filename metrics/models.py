from django.db import models

class blockchain(models.Model):
    hashcode = models.CharField(max_length=256,default="0")
    previoushash = models.CharField(max_length=256,default="0")
    data = models.CharField(max_length=500,default="0")
    date = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return self.data

# Create your models here.

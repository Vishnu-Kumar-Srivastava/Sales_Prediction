from django.db import models

#Create your models here.
class Feature(models.Model):
   name = models.CharField(max_length=20,default="hehe")
   details = models.CharField(max_length=500,null=True)
   
class Filename(models.Model):
   Filename = models.CharField(max_length = 200)
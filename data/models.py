from django.db import models

# Create your models here.

class User(models.Model):
    uid = models.AutoField(primary_key=True)
    user_auth = models.CharField(max_length = 100)
    salt = models.CharField(max_length=100)

class UserLocation(models.Model):
    user = models.ForeignKey(User)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

class Group(models.Model):
    gid = models.AutoField(primary_key=True)
    name = models.CharField(max_length = 100)
    password = models.CharField(max_length=100)
    salt = models.CharField(max_length=100)

class GroupMember(models.Model):
    group = models.ForeignKey(Group)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    visible = models.BooleanField()

class Global(models.Model):
    groups = models.IntegerField() 
    users = models.IntegerField()
    

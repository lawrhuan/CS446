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
    timestamp = models.IntegerField(null=True)

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

class UserMarker(models.Model):
    mid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.IntegerField()
    style = models.IntegerField()
    text = models.CharField(max_length=200)   

class Message(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    text = models.CharField(max_length=500)
    timestamp = models.IntegerField()

class Drawing(models.Model):
    did = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)
    timestamp = models.IntegerField()
    removed = models.BooleanField()

class DrawingPoint(models.Model):
    drawing = models.ForeignKey(Drawing)
    order = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()


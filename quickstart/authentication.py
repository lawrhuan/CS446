from django.shortcuts import render
from data.models import User, Group, GroupMember, UserLocation, UserMarker
from rest_framework import viewsets
from quickstart.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import uuid
import hashlib
import logging
import time


#helper functions
def generate_hash(string):
    #return hashlib.sha224(string).hexdigest()
    return string +'-hashed'

def authenticate_user(uid, user_auth):
    try:
        user = User.objects.get(uid=uid)
    except:
        return False

    if generate_hash(user.salt+ user_auth) == user.user_auth:
	return user
    else:
	return False

def authenticate_group(gid, password):
    try:
        group = Group.objects.get(gid=gid)
    except:
        return False

    logging.debug('HASHED: [');
    logging.debug(generate_hash(password));
    logging.debug('SERVER HASHED: [');
    logging.debug(group.password);
    if generate_hash(password) == group.password:
        return group
    else:
        return False

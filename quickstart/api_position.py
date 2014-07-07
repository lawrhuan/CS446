from django.shortcuts import render
from data.models import User, Group, GroupMember, UserLocation, UserMarker
from rest_framework import viewsets
from quickstart.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from quickstart.authentication import authenticate_user, authenticate_group, generate_hash


import datetime
import json
import uuid
import hashlib
import logging
import time

def request_positions(params):
    if not ('UID' in params and 'GID' in params and 'UserAuth' in params and 'Password' in params and 'Timestamp' in params):
        return {'error':'missing params'}
    
    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}

    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}

    if not GroupMember.objects.filter(group = group, user = user):
	return {'error': 'user not in group'}

    group_members = GroupMember.objects.filter(group = group, visible=1)
    group_positions = []

    current_time = int(time.time())
    for group_member in group_members:
	position={}
	group_user = group_member.user
	location = UserLocation.objects.get(user = group_user)
	if group_user == user or location.longitude == None or location.latitude==None or location.timestamp < params['Timestamp'] :
	    continue
	position['UserDisplayName'] = group_member.name
	position['Longitude'] = location.longitude
	position['Latitude'] = location.latitude	
	position['UID'] = group_user.uid
	group_positions.append(position)

    return {'Users':group_positions, 'Timestamp':current_time}

def send_position(params):
    if not ('UID' in params and 'UserAuth' in params and 'Latitude' in params and 'Longitude' in params and 'GIDs' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group_members = GroupMember.objects.filter(user=user)
    for group_member in group_members:
	if int(group_member.group.gid) in params['GIDs']:
	    group_member.visible = True
	else:
	    group_member.visible = False
	group_member.save()
    user_location = UserLocation.objects.filter(user=user).update(timestamp=int(time.time()),longitude=params['Longitude'], latitude = params['Latitude'])
    return {'valid':1}


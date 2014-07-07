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

def add_marker(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'Latitude' in params and 'Longitude' in params and 'Text' in params and 'Style' in params): 
	return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}

    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}
    user_marker = UserMarker.objects.create(group = group, user=user, latitude=params['Latitude'], longitude=params['Longitude'], text = params['Text'], style=params['Style'], timestamp=int(time.time()))
    return {'MID':user_marker.mid}

def remove_marker(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'MID' in params):
	return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}

    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}

#    if not UserMarker.objects.get(mid=params['mid']).user == user:
#	return {'error':'user did not create this marker'}	

    UserMarker.objects.filter(mid=params['MID']).delete()
    return {'valid':1}

def request_markers(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'Timestamp' in params):
        return {'error':'missing params'}
    
    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    current_time = int(time.time())

    group_markers = UserMarker.objects.filter(group = group)
    response = {'Timestamp':current_time, 'UID':[], 'Latitude':[],'Longitude':[],'Text':[], 'Style':[], 'MID':[],'OldMID':[]}
    for marker in group_markers:
	if marker.timestamp < params['Timestamp']:
	    response['OldMID'].append(marker.mid)
	    continue
	response['MID'].append(marker.mid)
    	response['UID'].append(marker.user.uid)
	response['Latitude'].append(marker.latitude)
	response['Longitude'].append(marker.longitude)
	response['Text'].append(marker.text)
	response['Style'].append(marker.style)

    return response
    

from django.shortcuts import render
from data.models import User, Group, GroupMember, UserLocation, UserMarker, Message
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

def send_text(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'Text' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}
    
    message = Message.objects.create(group=group, user=user, text=params['Text'], timestamp=int(time.time()))
    return {'valid':1}

def request_text(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'Timestamp' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}

    current_time = int(time.time())

    messages = Message.objects.filter(group = group, timestamp__gt = params['Timestamp']).order_by('timestamp')
    response = {'Timestamp':current_time, 'Users':[], 'Texts':[], 'Timestamps':[]}
    for message in messages:
	name = GroupMember.objects.get(group = group, user = message.user).name
        response['Users'].append(name)
        response['Texts'].append(message.text)
        response['Timestamps'].append(message.timestamp)
    return response


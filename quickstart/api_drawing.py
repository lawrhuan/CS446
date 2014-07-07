from django.shortcuts import render
from data.models import User, Group, GroupMember, UserLocation, UserMarker, Drawing, DrawingPoint
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

def request_drawings(params):
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

    drawings = Drawing.objects.filter(group=group, timestamp__gt=params['Timestamp'])
    current_time = int(time.time())
    rs = {'Drawings':[],'RemovedDrawings':[], 'Timestamp':current_time}
    for drawing in drawings:
        if drawing.removed:
	    rs['RemovedDrawings'].append(drawing.did)
    	    continue
        
        drawing_data = {'DID':drawing.did, 'Polyline':[], 'UID':drawing.user.uid, 'UserDisplayName':GroupMember.objects.get(group=group,user=user).name}

        points = DrawingPoint.objects.filter(drawing=drawing).order_by('order')
        for point in points:
	    drawing_data['Polyline'].append([point.latitude,point.longitude ])

        rs['Drawings'].append(drawing_data)
        
    return rs

def send_drawing(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'Drawing' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}

    drawing = Drawing.objects.create(group=group,user=user,timestamp=int(time.time()), removed=False)    
    for order, coordinate in enumerate(params['Drawing']):
	DrawingPoint.objects.create(drawing=drawing, order=order, longitude=coordinate[1], latitude=coordinate[0])
    return {'valid':1, 'DID':drawing.did}


def remove_drawing(params):
    if not ('UID' in params and 'UserAuth' in params and 'GID' in params and 'Password' in params and 'DID' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}
    
    drawing = Drawing.objects.filter(group=group, user=user, did=params['DID'])
    if not drawing:
	return {'warning':'Drawing Does not Exist'}

    coordinates = DrawingPoint.objects.filter(drawing=drawing).delete()
    drawing.update(removed=True, timestamp=int(time.time()))

    return {'valid':1}



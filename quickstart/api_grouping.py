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


def create_group(params):
    if not ('UID' in params and 'Password' in params and 'GroupName' in params and 'UserAuth' in params and 'UserDisplayName' in params and 'Salt' in params):
	return {'error':'missing params'}
    
    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
	return {'error':'unable to authenticate user'}
    
    new_group = Group.objects.create(name=params['GroupName'], password= generate_hash(params['Password']), salt=params['Salt'])
    new_member = GroupMember.objects.create(group = new_group, user=user, name=params['UserDisplayName'], visible=False)

    return {'GID':new_group.gid}


def list_groups(params):
    group_list = []
    groups = []
    if 'Query' in params:
	groups = Group.objects.filter(name__icontains=params['Query'])
    else:
        groups = Group.objects.all()
    for group in groups:
	group_dict = {}
	group_dict['GID']=group.gid
	group_dict['GroupName']=group.name
	group_list.append(group_dict)
    return {'Groups':group_list}


def request_members(params):
    if not ('UID' in params and 'Password' in params and 'GID' in params and 'UserAuth' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}
    if not GroupMember.objects.filter(group = group, user = user):
        return {'error': 'user not in group'}

    group_members = GroupMember.objects.filter(group = group)    
    rs = {'UID':[], 'UserDisplayName':[]}

    for group_member in group_members:
	rs['UID'].append(group_member.user.uid)
	rs['UserDisplayName'].append(group_member.name)

    return rs


def create_user(params):
    user_auth = str(uuid.uuid4())
    salt = str(uuid.uuid4())
    new_user = User.objects.create(user_auth = generate_hash(salt + user_auth), salt = salt)
    user_location = UserLocation.objects.create(user = new_user)
    return {'UID':new_user.uid,'UserAuth':user_auth}


def join_group_salt(params):
    if not ('GID' in params and 'UID' in params and 'UserAuth' in params):
        return {'error':'missing params'}

    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}
    group = Group.objects.get(gid=params['GID'])
    return {'Salt':group.salt}


def join_group(params):
    if not ('GID' in params and 'UID' in params and 'UserAuth' in params and 'Password' in params and 'UserDisplayName' in params):
	return {'error':'missing params'}
    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}

    group = authenticate_group(params['GID'], params['Password'])
    if not group:
        return {'error':'unable to authenticate group'}

    if GroupMember.objects.filter(group = group,user=user):
	return {'warning':'user already in group'}
    if GroupMember.objects.filter(group = group, name=params['UserDisplayName']):
  	return {'error':'name already in use'}
    new_member = GroupMember.objects.create(group = group, user=user, name=params['UserDisplayName'], visible=False)
    return {'valid':1}


def leave_group(params):
    if not ('UID' in params and 'GID' in params and 'UserAuth' in params):
    	return {'error':'missing params'}
    
    user = authenticate_user(params['UID'], params['UserAuth'])
    if not user:
        return {'error':'unable to authenticate user'}

    try:
	group = Group.objects.get(gid=params['GID'])
    except:
	return {'error':'invalid group'}

    GroupMember.objects.filter(group = group, user = user).delete()
    return {'valid':1}

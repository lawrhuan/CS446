from django.shortcuts import render
from data.models import User, Group, GroupMember, UserLocation, UserMarker, Message
from rest_framework import viewsets
from quickstart.serializers import UserSerializer, GroupSerializer
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from quickstart.authentication import authenticate_user, authenticate_group, generate_hash
from quickstart.api_grouping import create_user, create_group, join_group, leave_group, join_group_salt, list_groups, request_members
from quickstart.api_position import request_positions, send_position
from quickstart.api_marking import request_markers, remove_marker, add_marker
from quickstart.api_messaging import send_text, request_text
from quickstart.api_drawing import send_drawing, request_drawings, remove_drawing

import datetime
import json
import uuid
import hashlib
import logging
import time

# calls different request handler functions based on 'data.rq' URL parameter
#@method_decorator(csrf_exempt)
def process_request(request):
    logging.basicConfig(filename='/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/quickstart/req.log',level=logging.DEBUG, format='%(asctime)s:    %(message)s')

    rs = {}
    data = {}
    if request.method == 'GET':
	# get requests for testing
        data = request.GET.get('data',{'error':'request has no data parameter'})
	data = json.loads(data)
    elif request.method == 'POST':
    	try:
	    data = json.loads(request.body)
            logging.debug('----------- NEW REQUEST ---------------');
            logging.debug(str(data));
    	except ValueError, e:
	    data = request.GET.get('data',{'error':"request body is not valid json"})
    
    if 'error' in data:
	rs['error'] = data['error']
    elif 'TYPE' in data:
    	if data['TYPE'] == 'CreateGroup':
	    rs = create_group(data)
    	elif data['TYPE'] =='CreateUser':
	    rs = create_user(data)
	elif data['TYPE'] == 'ListGroups':
	    rs = list_groups(data)
	elif data['TYPE'] == 'JoinGroupSalt':
            rs = join_group_salt(data)
        elif data['TYPE'] == 'JoinGroup':
	    rs = join_group(data)
        elif data['TYPE'] == 'LeaveGroup':
	    rs = leave_group(data)
 	elif data['TYPE'] == 'RequestMembers':
            rs = request_members(data)
	elif data['TYPE'] == 'SendPosition':
	    rs = send_position(data)
	elif data['TYPE'] == 'RequestPositions':
	    rs = request_positions(data)
	elif data['TYPE'] == 'AddMarker':
	    rs = add_marker(data)
	elif data['TYPE'] == 'RemoveMarker':
	    rs = remove_marker(data)
	elif data['TYPE'] == 'RequestMarkers':
	    rs = request_markers(data)
	elif data['TYPE'] == 'SendText':
            rs = send_text(data)
   	elif data['TYPE'] == 'RequestText':
            rs = request_text(data)
	elif data['TYPE'] == 'SendDrawing':
            rs = send_drawing(data)
	elif data['TYPE'] == 'RequestDrawings':
            rs = request_drawings(data)
	elif data['TYPE'] == 'RemoveDrawing':
            rs = remove_drawing(data)
	else:
	    rs = {'error':'invalid type'}
    else:
	rs['error']='request missing TYPE field'

    #logging:
    logging.debug('-------------  NEW RESPONSE ------------');
    logging.debug(str(json.dumps(rs)));
    logging.debug('=====================================================');
    logging.debug('=====================================================');
    #end of logging:

    return HttpResponse(json.dumps(rs), content_type="application/json")

def showlog(request):
    with open ("/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/quickstart/req.log", "r") as myfile:
        data=myfile.read().replace('\n', '<br/>')
    return HttpResponse(data)
   
def clearlog(request):
   open('/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/quickstart/req.log', 'w').close()
   return HttpResponse("Cleared")

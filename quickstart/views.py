from django.shortcuts import render
#from django.contrib.auth.models import User, Group
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
#	return HttpResponse(json.dumps(data), content_type="application/json")
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

# request handler functions 
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
    groups = Group.objects.all()
    for group in groups:
	group_dict = {}
	group_dict['GID']=group.gid
	group_dict['GroupName']=group.name
	group_list.append(group_dict)
    return {'Groups':group_list}

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
    

def showlog(request):
    with open ("/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/quickstart/req.log", "r") as myfile:
        data=myfile.read().replace('\n', '<br/>')
    return HttpResponse(data)
   
def clearlog(request):
   open('/var/www/ec2-54-200-196-237.us-west-2.compute.amazonaws.com/quickstart/req.log', 'w').close()
   return HttpResponse("Cleared")

from django.contrib import admin
from data.models import User, Group, GroupMember, Global, UserLocation


# Register your models here.

admin.site.register(User)
admin.site.register(UserLocation)
admin.site.register(Group)
admin.site.register(GroupMember)
admin.site.register(Global)


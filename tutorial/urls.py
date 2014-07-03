from django.conf.urls import patterns, url, include
from rest_framework import routers
from quickstart import views
from django.contrib import admin

router = routers.DefaultRouter()
admin.autodiscover()
#router.register(r'users', views.UserViewSet)
#router.register(r'groups', views.GroupViewSet)
#router.register(r'create_user', views.CreateUserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
#    url(r'^', include(router.urls)),
    url(r'^admin', include(admin.site.urls)),
    url(r'^log', 'quickstart.views.showlog'),
    url(r'^clearlog', 'quickstart.views.clearlog'),
    url(r'^', 'quickstart.views.process_request'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

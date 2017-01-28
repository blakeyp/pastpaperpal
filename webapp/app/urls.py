from django.conf.urls import url, include
from . import views

app_name = 'app'

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^upload/$', views.upload, name='upload'),

    url(r'^get_modules/$', views.get_modules, name='get_modules'),

    # matches '/<module_code>/' url
    url(r'^(?P<module>.{5})/', include([
    	url(r'^$', views.module, name='module'),

    	# matches '/<module_code>/<year>/' url
    	url(r'^(?P<year>[0-9]{2})/', include([
    		url(r'^$', views.paper, name='paper'),
    		url(r'^q(?P<q_num>[0-9]{1,2})/similar$', views.similar_qs, name='similar_qs'),
    	])),

    ])),

]
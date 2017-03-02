from django.conf.urls import url, include
from . import views

app_name = 'app'

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^sign_in/$', views.sign_in, name='sign_in'),

    url(r'^sign_out/$', views.sign_out, name='sign_out'),

    url(r'^upload/$', views.upload, name='upload'),

    # matches '/<module_code>/' url
    url(r'^(?P<module>.{5})/', include([
    	url(r'^$', views.module, name='module'),

    	# matches '/<module_code>/<year>/' url
    	url(r'^(?P<year>[0-9]{2})/', include([
    		url(r'^$', views.paper, name='paper'),
    		url(r'^q(?P<q_num>[0-9]{1,2})/similar$', views.similar_qs, name='similar_qs'),
            url(r'^q(?P<q_num>[0-9]{1,2})/$', views.question, name='question'),
            url(r'^q(?P<q_num>[0-9]{1,2})/save_notes$', views.save_notes, name='save_notes'),
            url(r'^q(?P<q_num>[0-9]{1,2})/set_completed$', views.set_completed, name='set_completed'),
    	])),

    ])),

]
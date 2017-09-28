from django.conf.urls import url
from rest_framework_swagger.views import get_swagger_view

import views


urlpatterns = [
    url(r'^$', get_swagger_view(title='Hasker API')),
    url(r'^questions/$', views.QuestionList.as_view(), name='questions'),
    url(r'^questions/(?P<pk>\d+)$', views.QuestionDetail.as_view(), name='question'),
    url(r'^questions/(?P<question_pk>\d+)/answers$', views.AnswerList.as_view(), name='answers'),
    url(r'^questions/(?P<question_pk>\d+)/answers/(?P<pk>\d+)$', views.AnswerDetail.as_view(), name='answer')
]

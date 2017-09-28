from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.new_view, name='new'),
    url(r'^hot$', views.hot_view, name='hot'),
    url(r'^signup$', views.signup_view, name='signup'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^settings$', views.settings_view, name='settings'),
    url(r'^ask$', views.ask_view, name='ask'),
    url(r'^question/(?P<slug>[^/]+)$', views.question_view, name='question'),
    url(r'^tag/(?P<name>[^/]+)$', views.tag_view, name='tag'),
    url(r'^search$', views.search_view, name='search'),
    url(r'^mark-answer/(?P<answer_id>\d+)$', views.mark_correct_answer, name='mark-answer'),
    url(r'^vote-question/(?P<question_id>\d+)/(?P<value>.+)$', views.vote_for_question_view, name='vote-question'),
    url(r'^vote-answer/(?P<answer_id>\d+)/(?P<value>.+)$', views.vote_for_answer_view, name='vote-answer')
]

# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.http import (
    HttpResponseRedirect, Http404, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden)
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import AnswerForm, AskForm, LoginForm, SettingsForm, SignupForm
from .models import Question, Tag, Answer, QuestionVote, AnswerVote


QUESTIONS_LIMIT = 100
ANSWERS_LIMIT = 150


@require_GET
def new_view(req):
    questions = Question.objects.prefetch_related('author', 'tags').annotate(answers_num=Count('answer'))\
        .order_by('-creation_date')[:QUESTIONS_LIMIT]
    paginator = Paginator(questions, 20)
    page_num = req.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()
    context = {'questions': page, 'hot_url': reverse('hot'), 'pages_url': reverse('new')+'?page='}
    return render(req, 'new.html', context)


@require_GET
def hot_view(req):
    questions = Question.objects.prefetch_related('author', 'tags').annotate(answers_num=Count('answer'))\
        .order_by('-rating', '-creation_date')[:QUESTIONS_LIMIT]
    paginator = Paginator(questions, 20)
    page_num = req.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()
    context = {'questions': page, 'new_url': reverse('new'), 'pages_url': reverse('hot')+'?page='}
    return render(req, 'hot.html', context)


@require_http_methods(['GET', 'POST'])
def signup_view(req):
    if req.method == 'POST':
        form = SignupForm(req.POST, req.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(req, username=username, password=password)
            auth.login(req, user)
            return HttpResponseRedirect(reverse('new'))
    else:
        form = SignupForm()
    return render(req, 'signup.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def login_view(req):
    if req.method == 'POST':
        form = LoginForm(req, data=req.POST)
        if form.is_valid():
            user = form.user
            auth.login(req, user)
            next_url = req.POST.get('next', '/')
            return HttpResponseRedirect(next_url)
    else:
        next_url = req.GET.get('next', '/')
        if next_url == reverse('logout'):
            next_url = '/'
        form = LoginForm(initial={'next': next_url})
    return render(req, 'login.html', {'form': form})


@require_POST
@login_required(login_url='/login')
def logout_view(req):
    auth.logout(req)
    return HttpResponseRedirect(reverse('new'))


@require_http_methods(['GET', 'POST'])
@login_required(login_url='/login')
def settings_view(req):
    user = req.user
    if req.method == 'POST':
        form = SettingsForm(user, req.POST, req.FILES)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            avatar = form.cleaned_data.get('avatar')
            if avatar:
                user.avatar = avatar
            user.save()
            return HttpResponseRedirect(reverse('settings'))
    else:
        form = SettingsForm(initial={'email': user.email})
    return render(req, 'settings.html', {'form': form})


@require_http_methods(['GET', 'POST'])
@login_required(login_url='/login')
def ask_view(req):
    if req.method == 'POST':
        form = AskForm(req.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            tags = form.cleaned_data.get('tags')
            question = Question.objects.create(title, text, req.user, tags)
            return HttpResponseRedirect(question.url())
    else:
        form = AskForm()
    return render(req, 'ask.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def question_view(req, slug):
    user = req.user
    if req.method == 'POST' and user.is_authenticated:
        form = AnswerForm(req.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            question = get_object_or_404(Question, slug=slug)
            Answer.objects.create(question=question, text=text, author=user)
            url = u'{0}://{1}{2}'.format(
                req.scheme, req.META['HTTP_HOST'], question.url())
            send_mail(
                u'Hasker: New answer!',
                u'Link: {0}'.format(url),
                settings.EMAIL_HOST_USER,
                [question.author.email],
                html_message=u'Link: <a href="{0}">{1}</a>'.format(url, question.title),
                fail_silently=True
            )
            return HttpResponseRedirect(question.url())
    else:
        form = AnswerForm()
    try:
        if user.is_authenticated:
            question = Question.objects.get(user, slug=slug)
            answers = question.get_answers(0, ANSWERS_LIMIT, user)
        else:
            question = Question.objects.get(slug=slug)
            answers = question.get_answers(0, ANSWERS_LIMIT)
    except Question.DoesNotExist:
        raise Http404()
    paginator = Paginator(answers, 30)
    page_num = req.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()
    context = {'question': question, 'answers': page, 'form': form, 'pages_url': reverse('question', kwargs={'slug': slug})+'?page='}
    return render(req, 'question.html', context)


@require_GET
def tag_view(req, name):
    tag = get_object_or_404(Tag, name=name)
    questions = tag.question_set.all().prefetch_related('author', 'tags').annotate(answers_num=Count('answer'))\
        .order_by('-rating', '-creation_date')[:QUESTIONS_LIMIT]
    paginator = Paginator(questions, 20)
    page_num = req.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()
    context = {'questions': page, 'pages_url': reverse('tag', kwargs={'name': name})+'?page='}
    return render(req, 'tag.html', context)


@require_GET
def search_view(req):
    query = req.GET.get('q', '').strip()
    if not query or len(query) > 50:
        return HttpResponseBadRequest()
    if query[:4].lower() == 'tag:':
        tag_name = query[4:].strip().lower()
        return HttpResponseRedirect(reverse('tag', kwargs={'name': tag_name}))
    questions = Question.objects.prefetch_related('author', 'tags').annotate(answers_num=Count('answer'))\
        .filter(Q(title__icontains=query) | Q(text__icontains=query))\
        .order_by('-rating', '-creation_date')[:QUESTIONS_LIMIT]
    paginator = Paginator(questions, 20)
    page_num = req.GET.get('page', 1)
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        raise Http404()
    context = {'query': query, 'questions': page, 'pages_url': reverse('search')+'?q={0}&page='.format(query)}
    return render(req, 'search.html', context)


@require_POST
def mark_correct_answer(req, answer_id):
    user = req.user
    if not user.is_authenticated:
        return HttpResponseForbidden()
    answer = get_object_or_404(Answer, id=answer_id)
    answer.mark_correct(user)
    return JsonResponse({'status': 'ok'})


@require_POST
def vote_for_question_view(req, question_id, value):
    user = req.user
    if not user.is_authenticated:
        return HttpResponseForbidden()
    question = get_object_or_404(Question, id=question_id)
    if question.author == user:
        return JsonResponse({'status': 'error', 'message': 'You cannot vote for your question'})
    if value == 'for':
        rating = question.vote(user, QuestionVote.POSITIVE)
    elif value == 'against':
        rating = question.vote(user, QuestionVote.NEGATIVE)
    else:
        return HttpResponseBadRequest()
    return JsonResponse({'status': 'ok', 'rating': rating})


@require_POST
def vote_for_answer_view(req, answer_id, value):
    user = req.user
    if not user.is_authenticated:
        return HttpResponseForbidden()
    answer = get_object_or_404(Answer, id=answer_id)
    if answer.author == user:
        return JsonResponse({'status': 'error', 'message': 'You cannot vote for your answer'})
    if value == 'for':
        rating = answer.vote(user, AnswerVote.POSITIVE)
    elif value == 'against':
        rating = answer.vote(user, AnswerVote.NEGATIVE)
    else:
        return HttpResponseBadRequest()
    return JsonResponse({'status': 'ok', 'rating': rating})

# -*- coding: utf-8 -*-
import os
import itertools

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class QuestionVote(models.Model):
    POSITIVE = 1
    NEGATIVE = -1
    _VALUE_CHOICES = (
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative')
    )
    question = models.ForeignKey('Question')
    user = models.ForeignKey('User')
    value = models.SmallIntegerField(choices=_VALUE_CHOICES)


class AnswerVote(models.Model):
    POSITIVE = 1
    NEGATIVE = -1
    _VALUE_CHOICES = (
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative')
    )
    answer = models.ForeignKey('Answer')
    user = models.ForeignKey('User')
    value = models.SmallIntegerField(choices=_VALUE_CHOICES)


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def url(self):
        return reverse('tag', args=[self.name])


class QuestionManager(models.Manager):

    @transaction.atomic
    def create(self, title, text, author, tag_names):
        question = super(QuestionManager, self).create(title=title, text=text, author=author)
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            question.tags.add(tag)
        question.save()
        return question

    @transaction.atomic
    def get(self, user=None, **kwargs):
        question = self.prefetch_related('author', 'tags').get(**kwargs)
        question.vote = None
        if user:
            try:
                question.vote = QuestionVote.objects.get(question=question, user=user).value
            except QuestionVote.DoesNotExist:
                pass
        return question


class Question(models.Model):

    objects = QuestionManager()

    _MAX_SLUG_LENGTH = 255

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=_MAX_SLUG_LENGTH, unique=True)
    text = models.TextField()
    author = models.ForeignKey('User')
    creation_date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)

    def get_answers(self, offset, limit, user=None):
        answers = self.answer_set.prefetch_related('author')[offset:offset+limit]
        if user:
            votes = AnswerVote.objects.filter(answer__in=answers, user=user)
        else:
            votes = []
        answerid_to_votevalue = {vote.answer_id: vote.value for vote in votes}
        for answer in answers:
            answer.vote = answerid_to_votevalue.get(answer.id, None)
        return answers

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.slug = self._get_unique_slug()
        super(Question, self).save(*args, **kwargs)

    def _get_unique_slug(self):
        slugified_title = slugify(self.title, True)
        unique_slug = slugified_title[:self._MAX_SLUG_LENGTH]
        for num in itertools.count(1):
            if not Question.objects.filter(slug=unique_slug).exists():
                break
            num = str(num)
            unique_slug = slugified_title[:self._MAX_SLUG_LENGTH - 1 - len(num)] + '-' + num
        return unique_slug

    def url(self):
        return reverse('question', args=[self.slug])


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    author = models.ForeignKey('User')
    is_correct = models.BooleanField(default=False)
    creation_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ('-rating', '-creation_date')


def _get_file_path(user, filename):
    return os.path.join('user_{0}'.format(user.username), filename)


class User(AbstractUser):
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to=_get_file_path)

    @transaction.atomic
    def mark_correct_answer(self, answer):
        if answer.question.author_id != self.id:
            raise ValueError()
        try:
            correct_answer = Answer.objects.get(question=answer.question_id, is_correct=True)
            correct_answer.is_correct = False
            correct_answer.save()
        except Answer.DoesNotExist:
            pass
        answer.is_correct = True
        answer.save()

    @transaction.atomic
    def vote_for_question(self, question, value):
        if question.author_id == self.id:
            raise ValueError()
        try:
            vote = QuestionVote.objects.get(question=question, user=self)
            if vote.value == value:
                question.rating -= vote.value
                question.save()
                vote.delete()
            else:
                question.rating += value - vote.value
                question.save()
                vote.value = value
                vote.save()
        except QuestionVote.DoesNotExist:
            QuestionVote.objects.create(question=question, user=self, value=value)
            question.rating += value
            question.save()
        return question.rating

    @transaction.atomic
    def vote_for_answer(self, answer, value):
        if answer.author_id == self.id:
            raise ValueError()
        try:
            vote = AnswerVote.objects.get(answer=answer, user=self)
            if vote.value == value:
                answer.rating -= vote.value
                answer.save()
                vote.delete()
            else:
                answer.rating += value - vote.value
                answer.save()
                vote.value = value
                vote.save()
        except AnswerVote.DoesNotExist:
            AnswerVote.objects.create(answer=answer, user=self, value=value)
            answer.rating += value
            answer.save()
        return answer.rating

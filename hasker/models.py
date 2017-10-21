# -*- coding: utf-8 -*-
import itertools

from django.conf import settings
from django.db import models, transaction
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    value = models.SmallIntegerField(choices=_VALUE_CHOICES)


class AnswerVote(models.Model):
    POSITIVE = 1
    NEGATIVE = -1
    _VALUE_CHOICES = (
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative')
    )
    answer = models.ForeignKey('Answer')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
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
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    creation_date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)

    @transaction.atomic
    def vote(self, user, value):
        if self.author_id == user.id:
            raise ValueError()
        try:
            vote = QuestionVote.objects.get(question=self, user=user)
            if vote.value == value:
                self.rating -= vote.value
                self.save()
                vote.delete()
            else:
                self.rating += value - vote.value
                self.save()
                vote.value = value
                vote.save()
        except QuestionVote.DoesNotExist:
            QuestionVote.objects.create(question=self, user=user, value=value)
            self.rating += value
            self.save()
        return self.rating

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
    question = models.ForeignKey(Question)
    text = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    is_correct = models.BooleanField(default=False)
    creation_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(default=0)

    class Meta:
        ordering = ('-rating', '-creation_date')

    @transaction.atomic
    def mark_correct(self, user):
        if self.question.author_id != user.id:
            raise ValueError()
        try:
            correct_answer = Answer.objects.get(question=self.question_id, is_correct=True)
            correct_answer.is_correct = False
            correct_answer.save()
        except self.DoesNotExist:
            pass
        self.is_correct = True
        self.save()

    @transaction.atomic
    def vote(self, user, value):
        if self.author_id == user.id:
            raise ValueError()
        try:
            vote = AnswerVote.objects.get(answer=self, user=user)
            if vote.value == value:
                self.rating -= vote.value
                self.save()
                vote.delete()
            else:
                self.rating += value - vote.value
                self.save()
                vote.value = value
                vote.save()
        except AnswerVote.DoesNotExist:
            AnswerVote.objects.create(answer=self, user=user, value=value)
            self.rating += value
            self.save()
        return self.rating


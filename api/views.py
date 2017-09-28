# -*- coding: utf-8 -*-
from rest_framework import generics
from rest_framework import filters

from hasker.models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer


class QuestionList(generics.ListCreateAPIView):
    """
    get:
    Return a list of the questions.

    post:
    Create a new question.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ('creation_date', 'rating')
    search_fields = ('title', 'text')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class QuestionDetail(generics.RetrieveAPIView):
    """
    get:
    Return a question.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerList(generics.ListCreateAPIView):
    """
    get:
    Return a list of the answers for a question.

    post:
    Create a new answer for a question.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_pk = self.kwargs['question_pk']
        return Answer.objects.filter(question=question_pk).order_by('-rating', '-creation_date')

    def perform_create(self, serializer):
        question_pk = self.kwargs['question_pk']
        serializer.save(question_id=question_pk, author=self.request.user)


class AnswerDetail(generics.RetrieveAPIView):
    """
    get:
    Return an answer.
    """
    serializer_class = AnswerSerializer

    def get_queryset(self):
        question_pk = self.kwargs['question_pk']
        return Answer.objects.filter(question=question_pk)

import base64
import json
from io import BytesIO

from PIL import Image

from django.urls import reverse
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile


class TestQuestions(TestCase):

    def setUp(self):
        password = 'g78t87gt89g'
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': password,
                'password2': password,
                'avatar': self._make_image_file()}
        self.client.post(reverse('signup'), data)

    @staticmethod
    def _make_image_file():
        file_ = BytesIO()
        Image.new('RGB', (250, 250)).save(file_, 'png')
        file_.seek(0)
        return SimpleUploadedFile('name.png', file_.read())

    def test_questions(self):
        # create a question
        data = json.dumps({
            'title': 'My Question',
            'text': 'My Text',
            'tags': ['python', 'c++', 'java']
        })
        resp = self.client.post(reverse('api:questions'), data, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        pk = resp.json()['id']

        # get a question
        resp = self.client.get(reverse('api:question', kwargs={'pk': pk}))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('api:question', kwargs={'pk': pk+1}))
        self.assertEqual(resp.status_code, 404)

        # get a list of the questions
        resp = self.client.get(reverse('api:questions')+'?ordering=-rating,-creation_date')
        self.assertEqual(resp.status_code, 200)


class TestAnswers(TestCase):

    def setUp(self):
        password = 'g78t87gt89g'
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': password,
                'password2': password,
                'avatar': self._make_image_file()}
        self.client.post(reverse('signup'), data)

        data = json.dumps({
            'title': 'My Question',
            'text': 'My Text',
            'tags': ['python', 'c++', 'java']
        })
        resp = self.client.post(reverse('api:questions'), data, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.question_pk = resp.json()['id']

    @staticmethod
    def _make_image_file():
        file_ = BytesIO()
        Image.new('RGB', (250, 250)).save(file_, 'png')
        file_.seek(0)
        return SimpleUploadedFile('name.png', file_.read())

    def test_answers(self):
        # create an answer
        data = json.dumps({
            'text': 'My Text'
        })
        resp = self.client.post(reverse('api:answers', kwargs={'question_pk': self.question_pk}),
                                data, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        pk = resp.json()['id']

        # get an answer
        resp = self.client.get(reverse('api:answer', kwargs={'question_pk': self.question_pk, 'pk': pk}))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get(reverse('api:answer', kwargs={'question_pk': self.question_pk, 'pk': pk + 1}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.get(reverse('api:answer', kwargs={'question_pk': self.question_pk+1, 'pk': pk}))
        self.assertEqual(resp.status_code, 404)

        # get a list of the answers
        resp = self.client.get(reverse('api:answers', kwargs={'question_pk': self.question_pk}))
        self.assertEqual(resp.status_code, 200)


class TestBasicAuth(TestCase):

    def test_basic_auth(self):
        self.password = 'g78t87gt89g'
        self.username = 'bob'
        data = {'username': self.username,
                'email': 'bob@mail.ru',
                'password': self.password,
                'password2': self.password,
                'avatar': self._make_image_file()}
        self.client.post(reverse('signup'), data)

        self.client.logout()

        headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode('{0}:{1}'.format(self.username, self.password))
        }
        data = json.dumps({
            'title': 'My Question',
            'text': 'My Text',
            'tags': ['python', 'c++', 'java']
        })
        resp = self.client.post(reverse('api:questions'), data, content_type='application/json')
        self.assertEqual(resp.status_code, 401)
        resp = self.client.post(reverse('api:questions'), data, content_type='application/json', **headers)
        self.assertEqual(resp.status_code, 201)

    @staticmethod
    def _make_image_file():
        file_ = BytesIO()
        Image.new('RGB', (250, 250)).save(file_, 'png')
        file_.seek(0)
        return SimpleUploadedFile('name.png', file_.read())

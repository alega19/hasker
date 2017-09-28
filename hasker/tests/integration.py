from io import BytesIO

import mock
from PIL import Image

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from hasker.models import Question, Answer


class TestAnonymousUser(TestCase):

    def test_logout(self):
        resp = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(resp.redirect_chain[0],
                         (reverse('login')+'?next='+reverse('logout'), 302))

    def test_settings(self):
        resp = self.client.post(reverse('settings'), follow=True)
        self.assertEqual(resp.redirect_chain[0],
                         (reverse('login')+'?next='+reverse('settings'), 302))

    def test_ask(self):
        resp = self.client.post(reverse('ask'), follow=True)
        self.assertEqual(resp.redirect_chain[0],
                         (reverse('login')+'?next='+reverse('ask'), 302))

    def test_mark_correct_answer(self):
        resp = self.client.post(reverse('mark-answer', kwargs={'answer_id': 42}))
        self.assertEqual(resp.status_code, 403)

    def test_vote_for_question(self):
        resp = self.client.post(reverse('vote-question', kwargs={'question_id': 42, 'value': 'for'}))
        self.assertEqual(resp.status_code, 403)

    def test_vote_for_answer(self):
        resp = self.client.post(reverse('vote-answer', kwargs={'answer_id': 42, 'value': 'for'}))
        self.assertEqual(resp.status_code, 403)


class TestAuthenticatedUser(TestCase):

    @staticmethod
    def _make_image_file():
        file_ = BytesIO()
        Image.new('RGB', (250, 250)).save(file_, 'png')
        file_.seek(0)
        return SimpleUploadedFile('name.png', file_.read())

    def test_authenticated_user(self):
        # create a user
        password = 'g78t87gt89g'
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': password,
                'password2': password,
                'avatar': self._make_image_file()}
        resp = self.client.post(reverse('signup'), data)
        self.assertRedirects(resp, reverse('new'))

        # visit the settings
        resp = self.client.get(reverse('settings'))
        self.assertEqual(resp.status_code, 200)

        # logout
        resp = self.client.post(reverse('logout'))
        self.assertRedirects(resp, reverse('new'))

        # visit the settings
        resp = self.client.get(reverse('settings'))
        self.assertRedirects(resp, reverse('login')+'?next='+reverse('settings'))

        # login
        data = {'username': 'bob',
                'password': password,
                'next': reverse('settings')}
        resp = self.client.post(reverse('login'), data)
        self.assertRedirects(resp, reverse('settings'))

        # visit the ask page
        resp = self.client.get(reverse('ask'))
        self.assertEqual(resp.status_code, 200)

        # ask questions
        data = {'title': 'WTF?',
                'text': 'What am I doing here?',
                'tags': 'python,golang,otus'}
        slugs = []
        for i in xrange(5):
            slug = 'wtf-{0:d}'.format(i) if i else 'wtf'
            resp = self.client.post(reverse('ask'), data)
            self.assertRedirects(resp, reverse('question', kwargs={'slug': slug}))
            slugs.append(slug)

        # answer the own question
        data = {'text': 'My answer'}
        with mock.patch('hasker.views.send_mail') as send_mail:
            url = reverse('question', kwargs={'slug': slugs[-1]})
            resp = self.client.post(url, data, HTTP_HOST='example.com')
            send_mail.assert_called_once()
            args, kwargs = send_mail.call_args
            self.assertTrue(url in kwargs['html_message'])
            self.assertRedirects(resp, url)

        # mark the correct answer
        answer_id = Answer.objects.get().id
        resp = self.client.post(reverse('mark-answer', kwargs={'answer_id': answer_id}))
        self.assertEqual(resp.status_code, 200)

        # logout
        resp = self.client.post(reverse('logout'))
        self.assertRedirects(resp, reverse('new'))

        # visit the questions
        for slug in slugs:
            resp = self.client.post(reverse('question', kwargs={'slug': slug}))
            self.assertEqual(resp.status_code, 200)

        # create another user
        password = '3940juc39h083h'
        data = {'username': 'alice',
                'email': 'alice@mail.ru',
                'password': password,
                'password2': password,
                'avatar': self._make_image_file()}
        resp = self.client.post(reverse('signup'), data)
        self.assertRedirects(resp, reverse('new'))

        # visit the questions
        for slug in slugs:
            resp = self.client.post(reverse('question', kwargs={'slug': slug}))
            self.assertEqual(resp.status_code, 200)

        # vote for question
        question_id = Question.objects.get(slug=slugs[-1]).id
        resp = self.client.post(reverse('vote-question',
                                        kwargs={'question_id': question_id, 'value': 'for'}))
        self.assertEqual(resp.status_code, 200)

        # vote against answer
        resp = self.client.post(reverse('vote-answer',
                                        kwargs={'answer_id': answer_id, 'value': 'against'}))
        self.assertEqual(resp.status_code, 200)

        # logout
        resp = self.client.post(reverse('logout'))
        self.assertRedirects(resp, reverse('new'))

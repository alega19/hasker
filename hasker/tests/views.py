from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import Http404

from hasker.models import User, Question, Tag
from hasker.views import (
    new_view, hot_view, question_view, tag_view, search_view)


class TestNewView(TestCase):

    def setUp(self):
        super(TestNewView, self).setUp()
        self.factory = RequestFactory()
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123', avatar='blank.png')
        for _ in xrange(21):
            Question.objects.create('WTF?', 'LOL', user, [])

    def test_status_ok(self):
        req = self.factory.get(reverse('new'))
        resp = new_view(req)
        self.assertEqual(resp.status_code, 200)

        req = self.factory.get(reverse('new')+'?page=2')
        resp = new_view(req)
        self.assertEqual(resp.status_code, 200)

    def test_next_page_url(self):
        req = self.factory.get(reverse('new'))
        resp = new_view(req)
        self.assertContains(resp, reverse('new')+'?page=2')

    def test_prev_page_url(self):
        req = self.factory.get(reverse('new')+'?page=2')
        resp = new_view(req)
        self.assertContains(resp, reverse('new')+'?page=1')

    def test_hot_url(self):
        req = self.factory.get(reverse('new'))
        resp = new_view(req)
        self.assertContains(resp, reverse('hot'))


class TestHotView(TestCase):

    def setUp(self):
        super(TestHotView, self).setUp()
        self.factory = RequestFactory()
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123', avatar='blank.png')
        for _ in xrange(21):
            Question.objects.create('WTF?', 'LOL', user, [])

    def test_status_ok(self):
        req = self.factory.get(reverse('hot'))
        resp = hot_view(req)
        self.assertEqual(resp.status_code, 200)

        req = self.factory.get(reverse('hot')+'?page=2')
        resp = hot_view(req)
        self.assertEqual(resp.status_code, 200)

    def test_next_page_url(self):
        req = self.factory.get(reverse('hot'))
        resp = hot_view(req)
        self.assertContains(resp, reverse('hot')+'?page=2')

    def test_prev_page_url(self):
        req = self.factory.get(reverse('hot')+'?page=2')
        resp = hot_view(req)
        self.assertContains(resp, reverse('hot')+'?page=1')

    def test_new_url(self):
        req = self.factory.get(reverse('hot'))
        resp = hot_view(req)
        self.assertContains(resp, reverse('new'))


class TestQuestionView(TestCase):

    def setUp(self):
        super(TestQuestionView, self).setUp()
        self.factory = RequestFactory()
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123', avatar='blank.png')
        self.question = Question.objects.create('WTF?', 'LOL', user, [])
        for _ in xrange(31):
            self.question.answer_set.create(author=user, text='SPAM')

    def test_status_ok(self):
        req = self.factory.get(reverse('question', kwargs={'slug': self.question.slug}))
        req.user = AnonymousUser()
        resp = question_view(req, self.question.slug)
        self.assertEqual(resp.status_code, 200)

        req = self.factory.get(reverse('question', kwargs={'slug': self.question.slug})+'?page=2')
        req.user = AnonymousUser()
        resp = question_view(req, self.question.slug)
        self.assertEqual(resp.status_code, 200)

    def test_status_404(self):
        slug = self.question.slug+'z'
        req = self.factory.get(reverse('question', kwargs={'slug': slug}))
        req.user = AnonymousUser()
        self.assertRaises(Http404, lambda: question_view(req, slug))

    def test_next_page_url(self):
        req = self.factory.get(reverse('question', kwargs={'slug': self.question.slug}))
        req.user = AnonymousUser()
        resp = question_view(req, self.question.slug)
        self.assertContains(resp, reverse('question', kwargs={'slug': self.question.slug})+'?page=2')

    def test_prev_page_url(self):
        req = self.factory.get(reverse('question', kwargs={'slug': self.question.slug})+'?page=2')
        req.user = AnonymousUser()
        resp = question_view(req, self.question.slug)
        self.assertContains(resp, reverse('question', kwargs={'slug': self.question.slug})+'?page=1')


class TestTagView(TestCase):

    def setUp(self):
        super(TestTagView, self).setUp()
        self.factory = RequestFactory()
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123', avatar='blank.png')
        self.tag = Tag.objects.create(name='python')
        for _ in xrange(21):
            Question.objects.create('WTF?', 'LOL', user, ['python'])

    def test_status_ok(self):
        req = self.factory.get(reverse('tag', kwargs={'name': self.tag.name}))
        resp = tag_view(req, self.tag.name)
        self.assertEqual(resp.status_code, 200)

        req = self.factory.get(reverse('tag', kwargs={'name': self.tag.name})+'?page=2')
        resp = tag_view(req, self.tag.name)
        self.assertEqual(resp.status_code, 200)

    def test_status_404(self):
        slug = self.tag.name+'z'
        req = self.factory.get(reverse('tag', kwargs={'name': self.tag.name}))
        self.assertRaises(Http404, lambda: tag_view(req, slug))

    def test_next_page_url(self):
        req = self.factory.get(reverse('tag', kwargs={'name': self.tag.name}))
        resp = tag_view(req, self.tag.name)
        self.assertContains(resp, reverse('tag', kwargs={'name': self.tag.name})+'?page=2')

    def test_prev_page_url(self):
        req = self.factory.get(reverse('tag', kwargs={'name': self.tag.name})+'?page=2')
        resp = tag_view(req, self.tag.name)
        self.assertContains(resp, reverse('tag', kwargs={'name': self.tag.name})+'?page=1')


class TestSearchView(TestCase):

    def setUp(self):
        super(TestSearchView, self).setUp()
        self.factory = RequestFactory()
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123', avatar='blank.png')
        for _ in xrange(21):
            Question.objects.create('WTF?', 'LOL', user, [])

    def test_status_ok(self):
        req = self.factory.get(reverse('search')+'?q=LOL')
        resp = search_view(req)
        self.assertEqual(resp.status_code, 200)

        req = self.factory.get(reverse('search')+'?q=LOL&page=2')
        resp = search_view(req)
        self.assertEqual(resp.status_code, 200)

    def test_empty_query(self):
        req = self.factory.get(reverse('search'))
        resp = search_view(req)
        self.assertEqual(resp.status_code, 400)

    def test_next_page_url(self):
        req = self.factory.get(reverse('search') + '?q=LOL')
        resp = search_view(req)
        self.assertContains(resp, reverse('search')+'?q=LOL&amp;page=2')

    def test_prev_page_url(self):
        req = self.factory.get(reverse('search') + '?q=LOL&page=2')
        resp = search_view(req)
        self.assertContains(resp, reverse('search')+'?q=LOL&amp;page=1')

    def test_search_by_tag(self):
        req = self.factory.get(reverse('search') + '?q=tag:LOL')
        resp = search_view(req)
        self.assertEqual(resp.status_code, 302)

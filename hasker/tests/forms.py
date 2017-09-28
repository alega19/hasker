from io import BytesIO

from PIL import Image

from django.test import SimpleTestCase, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from hasker.forms import SignupForm, SettingsForm, AskForm
from hasker.models import User


class TestSignupForm(TestCase):

    def setUp(self):
        super(TestSignupForm, self).setUp()
        file_ = BytesIO()
        Image.new('RGB', (250, 250)).save(file_, 'png')
        file_.seek(0)
        png_file = SimpleUploadedFile('name.png', file_.read())
        self.files = {'avatar': png_file}

    def test_correct_data(self):
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': '186r128f7c222c',
                'password2': '186r128f7c222c'}
        form = SignupForm(data, self.files)
        self.assertTrue(form.is_valid())

    def test_too_simple_password(self):
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': '72164971649',
                'password2': '72164971649'}
        form = SignupForm(data, self.files)
        self.assertFalse(form.is_valid())

        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': 'gesgsegegwykf',
                'password2': 'gesgsegegwykf'}
        form = SignupForm(data, self.files)
        self.assertFalse(form.is_valid())

    def test_different_passwords(self):
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': '186r128f7c222c',
                'password2': 'Z186r128f7c222c'}
        form = SignupForm(data, self.files)
        self.assertFalse(form.is_valid())

    def test_existing_username(self):
        User.objects.create(username='bob', email='bob@yandex.ru', password='123')
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': '186r128f7c222c',
                'password2': '186r128f7c222c'}
        form = SignupForm(data, self.files)
        self.assertFalse(form.is_valid())

    def test_existing_email(self):
        User.objects.create(username='bob42', email='bob@mail.ru', password='123')
        data = {'username': 'bob',
                'email': 'bob@mail.ru',
                'password': '186r128f7c222c',
                'password2': '186r128f7c222c'}
        form = SignupForm(data, self.files)
        self.assertFalse(form.is_valid())


class TestSettingsForm(TestCase):

    def test_correct_data(self):
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        data = {'email': 'superstar@mail.ru'}
        form = SettingsForm(bob, data)
        self.assertTrue(form.is_valid())

    def test_existing_email(self):
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        alice = User.objects.create(username='alice', email='alice@mail.ru', password='123')
        data = {'email': bob.email}
        form = SettingsForm(alice, data)
        self.assertFalse(form.is_valid())


class TestAskForm(SimpleTestCase):

    def test_correct_tags_field(self):
        data = {'title': 'WTF?', 'text': 'OK', 'tags': 'one,two,three'}
        form = AskForm(data)
        self.assertTrue(form.is_valid())

        data = {'title': 'WTF?', 'text': 'OK', 'tags': 'one,two,three,'}
        form = AskForm(data)
        self.assertTrue(form.is_valid())

        data = {'title': 'WTF?', 'text': 'OK', 'tags': 'one,two, ,three'}
        form = AskForm(data)
        self.assertTrue(form.is_valid())

        data = {'title': 'WTF?', 'text': 'OK', 'tags': 'one,two,,,three'}
        form = AskForm(data)
        self.assertTrue(form.is_valid())

        data = {'title': 'WTF?', 'text': 'OK', 'tags': ''}
        form = AskForm(data)
        self.assertTrue(form.is_valid())

    def test_too_many_tags(self):
        data = {'title': 'WTF?', 'text': 'OK', 'tags': 'one,two,three,four'}
        form = AskForm(data)
        self.assertFalse(form.is_valid())

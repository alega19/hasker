from django.contrib.auth import get_user_model
from django.test import TestCase

from hasker.models import Tag, QuestionVote, AnswerVote


User = get_user_model()


class TestQuestion(TestCase):

    def test_questions_with_the_same_title(self):
        title = 'title'
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question1 = user.question_set.create(title=title, text='T', tag_names=[])
        question2 = user.question_set.create(title=title, text='T', tag_names=[])
        self.assertNotEqual(question1.slug, question2.slug)

    def test_creation_tags(self):
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        Tag(name='tag1').save()
        user.question_set.create(title='Q?', text='T', tag_names=['tag1', 'tag2'])
        self.assertEqual(Tag.objects.count(), 2)


class TestUser(TestCase):

    def test_mark_correct_answer(self):
        user = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question = user.question_set.create(title='Q?', text='T', tag_names=[])
        a1 = question.answer_set.create(author=user, text='T')
        a2 = question.answer_set.create(author=user, text='T')
        self.assertFalse(a1.is_correct)
        self.assertFalse(a2.is_correct)

        a1.mark_correct(user)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertTrue(a1.is_correct)
        self.assertFalse(a2.is_correct)

        a2.mark_correct(user)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertFalse(a1.is_correct)
        self.assertTrue(a2.is_correct)

    def test_vote_for_question(self):
        alice = User.objects.create(username='alice', email='alice@mail.ru', password='123')
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question = bob.question_set.create(title='?', text='T', tag_names=[])
        self.assertRaises(ValueError, lambda: question.vote(bob, QuestionVote.POSITIVE))
        question.refresh_from_db()
        self.assertEqual(question.rating, 0)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 0)

        question.vote(alice, QuestionVote.POSITIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, 1)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 1)

        question.vote(alice, QuestionVote.NEGATIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, -1)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 1)

        question.vote(alice, QuestionVote.NEGATIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, 0)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 0)

    def test_vote_for_answer(self):
        alice = User.objects.create(username='alice', email='alice@mail.ru', password='123')
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question = bob.question_set.create(title='?', text='T', tag_names=[])
        answer = question.answer_set.create(author=bob, text='T')

        self.assertRaises(ValueError, lambda: answer.vote(bob, AnswerVote.POSITIVE))
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 0)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 0)

        answer.vote(alice, AnswerVote.POSITIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 1)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 1)

        answer.vote(alice, AnswerVote.NEGATIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, -1)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 1)

        answer.vote(alice, AnswerVote.NEGATIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 0)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 0)

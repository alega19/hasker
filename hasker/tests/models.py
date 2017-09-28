from django.test import TestCase

from hasker.models import User, Tag, QuestionVote, AnswerVote


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

        user.mark_correct_answer(a1)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertTrue(a1.is_correct)
        self.assertFalse(a2.is_correct)

        user.mark_correct_answer(a2)
        a1.refresh_from_db()
        a2.refresh_from_db()
        self.assertFalse(a1.is_correct)
        self.assertTrue(a2.is_correct)

    def test_vote_for_question(self):
        alice = User.objects.create(username='alice', email='alice@mail.ru', password='123')
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question = bob.question_set.create(title='?', text='T', tag_names=[])
        self.assertRaises(ValueError, lambda: bob.vote_for_question(question, QuestionVote.POSITIVE))
        question.refresh_from_db()
        self.assertEqual(question.rating, 0)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 0)

        alice.vote_for_question(question, QuestionVote.POSITIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, 1)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 1)

        alice.vote_for_question(question, QuestionVote.NEGATIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, -1)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 1)

        alice.vote_for_question(question, QuestionVote.NEGATIVE)
        question.refresh_from_db()
        self.assertEqual(question.rating, 0)
        self.assertEqual(QuestionVote.objects.filter(question=question).count(), 0)

    def test_vote_for_answer(self):
        alice = User.objects.create(username='alice', email='alice@mail.ru', password='123')
        bob = User.objects.create(username='bob', email='bob@mail.ru', password='123')
        question = bob.question_set.create(title='?', text='T', tag_names=[])
        answer = question.answer_set.create(author=bob, text='T')

        self.assertRaises(ValueError, lambda: bob.vote_for_answer(answer, AnswerVote.POSITIVE))
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 0)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 0)

        alice.vote_for_answer(answer, AnswerVote.POSITIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 1)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 1)

        alice.vote_for_answer(answer, AnswerVote.NEGATIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, -1)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 1)

        alice.vote_for_answer(answer, AnswerVote.NEGATIVE)
        answer.refresh_from_db()
        self.assertEqual(answer.rating, 0)
        self.assertEqual(AnswerVote.objects.filter(answer=answer).count(), 0)

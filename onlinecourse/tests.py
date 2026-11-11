from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Enrollment, Lesson, Question, Submission


class AssessmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.learner = users.create_user(username="learner")
        cls.other = users.create_user(username="other")
        cls.admin = users.create_superuser(username="staff")
        cls.course = Course.objects.create(name="Django and SQL")
        cls.another_course = Course.objects.create(name="Different course")
        Lesson.objects.create(course=cls.course, title="SQL queries")
        cls.enrollment = Enrollment.objects.create(course=cls.course, user=cls.learner)
        question = Question.objects.create(course=cls.course, question_text="Read rows?", grade=3)
        cls.correct = Choice.objects.create(question=question, choice_text="SELECT", is_correct=True)
        cls.wrong = Choice.objects.create(question=question, choice_text="DELETE")
        other_question = Question.objects.create(course=cls.another_course, question_text="Other?")
        cls.foreign_choice = Choice.objects.create(question=other_question, choice_text="Other")

    def setUp(self):
        self.client.force_login(self.learner)
        self.submit_url = reverse("onlinecourse:submit", args=[self.course.pk])

    def test_course_displays_related_lessons_and_exam(self):
        response = self.client.get(reverse("onlinecourse:course_details", args=[self.course.pk]))
        for text in ("Django and SQL", "SQL queries", "Read rows?", "Submit Exam"):
            self.assertContains(response, text)
        self.assertNotContains(response, "Other?")

    def test_submit_correct_answer_and_render_passing_result(self):
        response = self.client.post(self.submit_url, {"choice": [self.correct.pk]}, follow=True)
        self.assertEqual(Submission.objects.get().enrollment, self.enrollment)
        for text in ("Exam Results", "Congratulations!", "Score: 100.0%"):
            self.assertContains(response, text)

    def test_extra_wrong_choice_does_not_earn_credit(self):
        response = self.client.post(
            self.submit_url, {"choice": [self.correct.pk, self.wrong.pk]}, follow=True
        )
        self.assertContains(response, "Score: 0.0%")
        self.assertNotContains(response, "Congratulations!")

    def test_blank_attempt_scores_zero(self):
        response = self.client.post(self.submit_url, follow=True)
        self.assertContains(response, "Score: 0.0%")

    def test_invalid_or_foreign_choice_is_rejected(self):
        for choice in ("invalid", self.foreign_choice.pk):
            with self.subTest(choice=choice):
                self.assertEqual(self.client.post(self.submit_url, {"choice": choice}).status_code, 400)
        self.assertFalse(Submission.objects.exists())

    def test_unenrolled_user_cannot_submit(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.submit_url).status_code, 403)

    def test_anonymous_user_is_redirected_to_login(self):
        self.client.logout()
        self.assertEqual(self.client.post(self.submit_url).status_code, 302)
        self.assertFalse(Submission.objects.exists())

    def test_get_does_not_create_submission(self):
        self.assertEqual(self.client.get(self.submit_url).status_code, 405)
        self.assertFalse(Submission.objects.exists())

    def test_result_requires_ownership_and_matching_course(self):
        attempt = Submission.objects.create(enrollment=self.enrollment)
        for course, user in ((self.course, self.other), (self.another_course, self.learner)):
            self.client.force_login(user)
            url = reverse("onlinecourse:show_exam_result", args=[course.pk, attempt.pk])
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_admin_lists_both_sections_and_assessment_models(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:index"))
        for text in ("Authentication and Authorization", "OnlineCourse",
                     "Questions", "Choices", "Submissions"):
            self.assertContains(response, text)

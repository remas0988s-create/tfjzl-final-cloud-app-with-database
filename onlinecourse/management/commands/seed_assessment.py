"""Create a small course and exam for manual verification."""

from django.core.management.base import BaseCommand
from django.db import transaction

from onlinecourse.models import Choice, Course, Lesson, Question


class Command(BaseCommand):
    help = "Create a demo Django and SQL course for testing the assessment."

    @transaction.atomic
    def handle(self, *args, **options):
        course, _ = Course.objects.get_or_create(
            name="Django and SQL Demo",
            defaults={"description": "Practice queries and Django models."},
        )
        Lesson.objects.get_or_create(
            course=course, title="Querying a database",
            defaults={"order": 0, "content": "SELECT reads rows from a table."},
        )
        Lesson.objects.get_or_create(
            course=course, title="Django models",
            defaults={"order": 1, "content": "Models describe stored data."},
        )
        for prompt, answers in (
            ("Which SQL command reads rows?", [("SELECT", True), ("DELETE", False)]),
            ("Which Django field links a lesson to its course?",
             [("ForeignKey", True), ("BooleanField", False)]),
        ):
            question, _ = Question.objects.get_or_create(course=course, question_text=prompt)
            for answer, correct in answers:
                Choice.objects.get_or_create(
                    question=question, choice_text=answer, defaults={"is_correct": correct}
                )
        self.stdout.write(self.style.SUCCESS(f"Demo course: /onlinecourse/{course.pk}/"))

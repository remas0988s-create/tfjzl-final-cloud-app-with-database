from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
# <HINT> Import any new Models here
from .models import Choice, Course, Enrollment, Submission
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        context['lessons'] = course.lesson_set.order_by('order', 'pk')
        context['questions'] = course.question_set.prefetch_related('choice_set').order_by('pk')
        context['is_enrolled'] = check_if_enrolled(self.request.user, course)
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


@login_required(login_url="onlinecourse:login")
@require_POST
@transaction.atomic
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = Enrollment.objects.filter(course=course, user=request.user).order_by("pk").first()
    if enrollment is None:
        return HttpResponseForbidden("Enroll in this course before taking its exam.")
    if not course.question_set.exists():
        return HttpResponseBadRequest("This course does not have an exam.")
    try:
        choice_ids = {int(value) for value in request.POST.getlist("choice")}
    except ValueError:
        return HttpResponseBadRequest("Invalid answer selection.")
    choices = list(Choice.objects.filter(pk__in=choice_ids, question__course=course))
    if len(choices) != len(choice_ids):
        return HttpResponseBadRequest("Invalid answer selection.")
    submission = Submission.objects.create(enrollment=enrollment)
    submission.choices.set(choices)
    return redirect("onlinecourse:show_exam_result", course.id, submission.id)


@login_required(login_url="onlinecourse:login")
@require_GET
def show_exam_result(request, course_id, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("enrollment__course"),
        pk=submission_id,
        enrollment__course_id=course_id,
        enrollment__user=request.user,
    )
    course = submission.enrollment.course
    selected = set(submission.choices.values_list("pk", flat=True))
    earned = total = 0
    results = []
    for question in course.question_set.prefetch_related("choice_set").order_by("pk"):
        choices = list(question.choice_set.all())
        correct = {choice.pk for choice in choices if choice.is_correct}
        picked = {choice.pk for choice in choices if choice.pk in selected}
        is_correct = bool(correct) and picked == correct
        total += question.grade
        if is_correct:
            earned += question.grade
        results.append({
            "question": question,
            "is_correct": is_correct,
            "picked": [choice.choice_text for choice in choices if choice.pk in picked],
            "correct": [choice.choice_text for choice in choices if choice.pk in correct],
        })
    return render(request, "onlinecourse/exam_result_bootstrap.html", {
        "course": course, "results": results, "earned": earned, "total": total,
        "score": 100 * earned / total if total else 0,
        "passed": total > 0 and 100 * earned >= 80 * total,
    })

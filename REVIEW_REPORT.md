# مراجعة Final Project: Add a New Assessment Feature to an Online Course App

مصدر البداية هو [مستودع IBM الرسمي](https://github.com/ibm-developer-skills-network/tfjzl-final-cloud-app-with-database)، عند الالتزام 185b62358f6f6c4ac4d076158ce25d5b4dfc4236. العمل في Fork عام باسم remas0988s-create/tfjzl-final-cloud-app-with-database. طابقت المراجعة بنود الأسئلة السبعة المرسلة. أمكن التحقق من صفحة الكورس العامة وملفات القالب، وبقي نص اللاب داخل Coursera وتشغيل IBM Mark خارج نطاق التحقق الفعلي.

| السؤال | الدرجة | التحقق |
| --- | ---: | --- |
| 1 | 3 | [models.py](onlinecourse/models.py) يحتوي Question وChoice وSubmission. نجح تطبيق migration على SQLite. |
| 2 | 3 | [admin.py](onlinecourse/admin.py) يستورد Course وLesson وInstructor وLearner وQuestion وChoice وSubmission. يحتوي QuestionInline وChoiceInline وQuestionAdmin وLessonAdmin. |
| 3 | 1 | ظهر Authentication and Authorization وOnlineCourse في صفحة لوحة الإدارة الفعلية عبر HTTP. بقي التقاط 03-admin-site.png في المتصفح. |
| 4 | 2 | [course_details_bootstrap.html](onlinecourse/templates/onlinecourse/course_details_bootstrap.html) يعرض اسم الكورس والدروس والأسئلة باستخدام Django Template Tags وBootstrap. |
| 5 | 2 | [views.py](onlinecourse/views.py) يحتوي submit وshow_exam_result. اختُبر الحفظ والحساب وملكية النتيجة. |
| 6 | 2 | [urls.py](onlinecourse/urls.py) يربط المسارين بالدالتين. نجح إرسال النموذج ثم الانتقال للنتيجة. |
| 7 | 2 | ظهرت Exam Results وCongratulations وScore: 100.0% (2/2) في رد التطبيق بعد إرسال اختبار تجريبي فعلي. بقي التقاط 07-final.png في المتصفح. |

## كيف يعمل الكود

- `Question.course` مفتاح خارجي للكورس. `Choice.question` مفتاح خارجي للسؤال، و`is_correct` يحدد صحة الخيار. ترتبط المحاولة `Submission` بتسجيل الطالب `Enrollment`، وتحفظ اختياراته بعلاقة ManyToMany.
- في الإدارة تضيف `QuestionInline` أسئلة من صفحة الكورس، وتضيف `ChoiceInline` خيارات من صفحة السؤال. تسجّل `QuestionAdmin` طريقة عرض الأسئلة، و`LessonAdmin` طريقة عرض الدروس.
- القالب يعرض `{{ course.name }}` ويكرر الدروس بالوسم `{% for lesson in lessons %}`. نموذج الاختبار يرسل الخيارات مع CSRF.
- تتحقق `submit` من الدخول والتسجيل وانتماء الخيارات للكورس ثم تحفظ المحاولة. تعرض `show_exam_result` نتيجة محاولة صاحبها فقط. يحصل السؤال على نقاطه عند اختيار مجموعة الإجابات الصحيحة كاملة، وحد النجاح المستخدم 80%. تُحسب النتيجة من الأسئلة الحالية، لذا قد تتغير المحاولات القديمة إذا عدّل المسؤول الأسئلة أو الإجابات.

## نتائج التشغيل المحلي

استُخدم Django 5.2.19 مع SQLite. نجح `migrate`، ولم يبلغ `check` عن مشاكل، ولم يجد `makemigrations --check --dry-run` تغييرات معلقة. نجحت الاختبارات العشرة. تعطلت محاولة الفحص الشبكي الأولى بسبب غياب requests، ثم نجح الفحص باستخدام urllib على خادم Django محلي حقيقي. السجلان [اختبارات Django](validation/django-tests.txt) و[طلبات HTTP](validation/live-http.txt).

## تشغيل IBM Skills Network والتقاط الصورتين

افتحي **Final Project: Add a New Assessment Feature to an Online Course App** في Module 5، ثم افتحي Terminal داخل اللاب. إذا عندك نسخة عمل من قبل، راجعيها أولًا باستخدام git status. في مجلد جديد استخدمي هذه الأوامر مع Python 3.10 فأحدث.

```bash
git clone https://github.com/remas0988s-create/tfjzl-final-cloud-app-with-database.git
cd tfjzl-final-cloud-app-with-database
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py seed_assessment
python manage.py createsuperuser
```

إذا كان عنوان Application Launcher الخارجي هو `https://YOUR-LAB-HOST`، استخدمي اسم المضيف الفعلي في الإعداد الأول وأصله الكامل في الثاني.

```bash
export DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1,YOUR-LAB-HOST'
export DJANGO_CSRF_TRUSTED_ORIGINS='https://YOUR-LAB-HOST'
python manage.py runserver 0.0.0.0:8000
```

1. افتحي المنفذ 8000 في Application Launcher ثم أضيفي `/admin/` للرابط. سجّلي الدخول بحساب الإدارة الذي أنشأتيه. صوري الصفحة عندما يظهر القسمان معًا واحفظيها باسم **03-admin-site.png**.
2. افتحي مسار الكورس الذي طبعه `seed_assessment`. اضغطي Enroll، واختاري **SELECT** و**ForeignKey**، ثم Submit Exam. بعد ظهور العنوان والتهنئة والدرجة، التقطي **07-final.png**.
3. قارني اللقطتين والروابط العامة بنص IBM Mark الحالي قبل التسليم. التشغيل المثبت هنا محلي. لم يتم الدخول إلى جلسة اللاب الخاصة بك أو إرسال التقييم.

القالب من IBM والتعديلات والاختبارات أُعدت بمساعدة الذكاء الاصطناعي. راجعي الكود وأعيدي تشغيله بنفسك وتحققي من قواعد المساعدة الخاصة بالتكليف قبل استخدامه في تقييم.

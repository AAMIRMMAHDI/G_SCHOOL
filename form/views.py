# views.py کامل اصلاح‌شده (parse برای TextField – string ساده)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.db.models import F
from django.urls import reverse
from django.conf import settings
from webpush import send_user_notification
from .models import Class, Student, ClassSchedule, Attendance, Schedule, Exam, Question, StudentAnswer, Grade, Major, GradeLevel, EntryPermission, Notification, StudentRegistrationRequest
from .forms import ExamForm, EntryPermissionForm, StudentRegistrationForm

User = get_user_model()


def user_login(request):
    """ورود کاربر به سیستم"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'با موفقیت وارد شدید.')
            return redirect('form:class_list')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'form/Login.html')


@login_required
def class_list(request):
    """نمایش لیست کلاس‌های فعال معلم"""
    show_all = request.GET.get('show_all', False)
    today = timezone.now().strftime('%a')[:3]

    try:
        if show_all:
            class_schedules = ClassSchedule.objects.filter(teacher=request.user, day=today)
        else:
            now_time = timezone.localtime(timezone.now()).time()
            class_schedules = (
                ClassSchedule.objects.filter(
                    teacher=request.user,
                    day=today,
                    schedule__start_time__lte=now_time,
                    schedule__end_time__gte=now_time
                ) | ClassSchedule.objects.filter(teacher=request.user, day=today, schedule__zeng=5)
            )
        if not class_schedules.exists():
            messages.info(request, 'کلاسی برای امروز یافت نشد.')
    except Exception as e:
        messages.error(request, f'خطا در بارگذاری کلاس‌ها: {str(e)}')
        class_schedules = []

    return render(request, 'form/Class_list.html', {
        'class_schedules': class_schedules,
        'show_all': show_all
    })


@login_required
def attendance(request, class_schedule_id):
    """ثبت حضور و غیاب برای یک کلاس خاص"""
    try:
        class_schedule = get_object_or_404(ClassSchedule, id=class_schedule_id, teacher=request.user)

        if not class_schedule.is_active():
            messages.error(request, 'این زنگ تمام شده و نمی‌توانید حضور و غیاب را تغییر دهید.')
            return redirect('form:class_list')

        students = Student.objects.filter(class_obj=class_schedule.class_obj)
        if not students.exists():
            messages.warning(request, 'هیچ دانش‌آموزی برای این کلاس ثبت نشده است.')

        if request.method == 'POST':
            any_status_saved = False
            for student in students:
                status = request.POST.get(f'status_{student.id}')
                if status in ['P', 'A', 'L']:
                    Attendance.objects.update_or_create(
                        student=student,
                        class_schedule=class_schedule,
                        date=timezone.now().date(),
                        defaults={'status': status}
                    )
                    any_status_saved = True
                else:
                    messages.warning(request, f'وضعیت نامعتبر برای دانش‌آموز {student} دریافت شد.')
            if any_status_saved:
                messages.success(request, 'حضور و غیاب با موفقیت ثبت شد.')
            else:
                messages.error(request, 'هیچ وضعیت معتبری ثبت نشد.')
            return redirect('form:attendance', class_schedule_id=class_schedule_id)

        attendance_records = {
            a.student_id: a.status
            for a in Attendance.objects.filter(class_schedule=class_schedule, date=timezone.now().date())
        }

        return render(request, 'form/Current_List.html', {
            'class_schedule': class_schedule,
            'students': students,
            'attendance_records': attendance_records
        })
    except Exception as e:
        messages.error(request, f'خطا در ثبت حضور و غیاب: {str(e)}')
        return redirect('form:class_list')


@login_required
def weekly_schedule(request):
    """مدیریت برنامه هفتگی کلاس‌ها"""
    if not request.user.is_superuser:
        messages.error(request, 'شما مجاز به دسترسی به این صفحه نیستید.')
        return redirect('form:class_list')  # ریدایرکت به لیست کلاس‌ها اگر ادمین نبود

    classes = Class.objects.all()
    selected_class = None
    schedules = []
    days = [
        ('Sat', 'شنبه'),
        ('Sun', 'یک‌شنبه'),
        ('Mon', 'دوشنبه'),
        ('Tue', 'سه‌شنبه'),
        ('Wed', 'چهارشنبه'),
    ]
    zengs = Schedule.objects.exclude(zeng=5).order_by('zeng')

    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        if not class_id:
            messages.error(request, 'کلاس انتخاب نشده است.')
            return redirect('form:weekly_schedule')

        try:
            selected_class = get_object_or_404(Class, id=class_id)
            for day, _ in days:
                for zeng in zengs:
                    split_period = request.POST.get(f'split_{day}_{zeng.id}') == 'on'

                    if split_period:
                        teacher1_id = request.POST.get(f'teacher1_{day}_{zeng.id}')
                        subject1 = request.POST.get(f'subject1_{day}_{zeng.id}')
                        unit1 = request.POST.get(f'unit1_{day}_{zeng.id}')
                        teacher2_id = request.POST.get(f'teacher2_{day}_{zeng.id}')
                        subject2 = request.POST.get(f'subject2_{day}_{zeng.id}')
                        unit2 = request.POST.get(f'unit2_{day}_{zeng.id}')

                        ClassSchedule.objects.filter(
                            class_obj=selected_class,
                            schedule=zeng,
                            day=day,
                            is_split=False
                        ).delete()

                        if teacher1_id and subject1 and unit1:
                            ClassSchedule.objects.update_or_create(
                                class_obj=selected_class,
                                schedule=zeng,
                                day=day,
                                split_part=1,
                                defaults={
                                    'teacher': User.objects.get(id=teacher1_id),
                                    'subject': subject1,
                                    'unit': unit1,
                                    'is_split': True
                                }
                            )
                        else:
                            messages.warning(request, f'داده‌های نیمه اول برای {day}، زنگ {zeng.get_zeng_display()} کامل نیست.')
                        
                        if teacher2_id and subject2 and unit2:
                            ClassSchedule.objects.update_or_create(
                                class_obj=selected_class,
                                schedule=zeng,
                                day=day,
                                split_part=2,
                                defaults={
                                    'teacher': User.objects.get(id=teacher2_id),
                                    'subject': subject2,
                                    'unit': unit2,
                                    'is_split': True
                                }
                            )
                        else:
                            messages.warning(request, f'داده‌های نیمه دوم برای {day}، زنگ {zeng.get_zeng_display()} کامل نیست.')
                    else:
                        teacher_id = request.POST.get(f'teacher_{day}_{zeng.id}')
                        subject = request.POST.get(f'subject_{day}_{zeng.id}')
                        unit = request.POST.get(f'unit_{day}_{zeng.id}')

                        ClassSchedule.objects.filter(
                            class_obj=selected_class,
                            schedule=zeng,
                            day=day,
                            is_split=True
                        ).delete()

                        if teacher_id and subject and unit:
                            ClassSchedule.objects.update_or_create(
                                class_obj=selected_class,
                                schedule=zeng,
                                day=day,
                                split_part=0,
                                defaults={
                                    'teacher': User.objects.get(id=teacher_id),
                                    'subject': subject,
                                    'unit': unit,
                                    'is_split': False
                                }
                            )
                        else:
                            ClassSchedule.objects.filter(
                                class_obj=selected_class,
                                schedule=zeng,
                                day=day
                            ).delete()
                            messages.warning(request, f'داده‌های زنگ غیرتقسیم‌شده برای {day}، زنگ {zeng.get_zeng_display()} کامل نیست.')
            messages.success(request, 'برنامه هفتگی با موفقیت ثبت شد.')
        except Exception as e:
            messages.error(request, f'خطا در ثبت برنامه: {str(e)}')
        return redirect('form:weekly_schedule')

    if request.GET.get('class_id'):
        try:
            selected_class = get_object_or_404(Class, id=request.GET.get('class_id'))
            schedules = []
            for day, day_name in days:
                day_schedules = []
                for zeng in zengs:
                    split_schedules = ClassSchedule.objects.filter(
                        class_obj=selected_class,
                        schedule=zeng,
                        day=day,
                        is_split=True
                    ).order_by('split_part')

                    if split_schedules.exists():
                        day_schedules.append({
                            'zeng': zeng,
                            'is_split': True,
                            'first_half': split_schedules.filter(split_part=1).first(),
                            'second_half': split_schedules.filter(split_part=2).first()
                        })
                    else:
                        schedule = ClassSchedule.objects.filter(
                            class_obj=selected_class,
                            schedule=zeng,
                            day=day,
                            is_split=False
                        ).first()
                        day_schedules.append({
                            'zeng': zeng,
                            'is_split': False,
                            'schedule': schedule
                        })
                schedules.append({'day': day, 'day_name': day_name, 'periods': day_schedules})
        except Exception as e:
            messages.error(request, f'خطا در بارگذاری برنامه: {str(e)}')

    return render(request, 'form/Class_time.html', {
        'classes': classes,
        'selected_class': selected_class,
        'schedules': schedules,
        'days': days,
        'zengs': zengs,
        'teachers': User.objects.all()
    })


@login_required
def create_exam(request):
    """ایجاد آزمون جدید توسط معلم"""
    QuestionFormSet = inlineformset_factory(Exam, Question, fields=('text', 'option1', 'option2', 'option3', 'option4', 'correct_option'), extra=1, min_num=1, validate_min=True, can_delete=True)
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.teacher = request.user
            exam.save()
            formset = QuestionFormSet(request.POST, instance=exam)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'آزمون با موفقیت ایجاد شد. لینک اشتراک: ' + request.build_absolute_uri(reverse('form:take_exam', args=[exam.id])))
                return redirect('form:exam_list')
            else:
                messages.error(request, 'خطا در سوالات: ' + str(formset.errors))
        else:
            messages.error(request, 'خطا در فرم آزمون: ' + str(form.errors))
    else:
        form = ExamForm()
        formset = QuestionFormSet(queryset=Question.objects.none())

    return render(request, 'form/Test_making.html', {'form': form, 'formset': formset})


@login_required
def exam_list(request):
    """لیست آزمون‌های معلم"""
    exams = Exam.objects.filter(teacher=request.user)
    return render(request, 'form/Test_list.html', {'exams': exams})


def take_exam(request, exam_id):
    """شرکت در آزمون توسط دانش‌آموز با شناسایی ساده"""
    exam = get_object_or_404(Exam, id=exam_id)
    if not exam.is_ongoing():
        messages.error(request, 'این آزمون فعال نیست یا زمان آن تمام شده.')
        return redirect('form:class_list')

    student_id = request.session.get('student_id')
    student = None
    if student_id:
        student = get_object_or_404(Student, id=student_id, class_obj=exam.class_obj)

    if request.method == 'POST' and 'identify' in request.POST:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        row_number = request.POST.get('row_number')
        if first_name and last_name:
            try:
                student = Student.objects.get(
                    class_obj=exam.class_obj,
                    first_name__iexact=first_name,
                    last_name__iexact=last_name,
                    row_number=row_number if row_number else None
                )
                request.session['student_id'] = student.id
                messages.success(request, 'شناسایی موفق. حالا آزمون را شروع کنید.')
            except Student.DoesNotExist:
                messages.error(request, 'دانش‌آموز یافت نشد. اطلاعات را چک کنید.')
            except Student.MultipleObjectsReturned:
                messages.error(request, 'چند دانش‌آموز یافت شد. شماره کلاسی وارد کنید.')

    if not student:
        return render(request, 'form/Student_login.html', {'exam': exam})

    questions = exam.questions.all()
    if request.method == 'POST' and 'submit_answers' in request.POST:
        any_answer_saved = False
        for question in questions:
            selected = request.POST.get(f'answer_{question.id}')
            if selected and selected.isdigit() and 1 <= int(selected) <= 4:
                StudentAnswer.objects.update_or_create(
                    student=student,
                    question=question,
                    defaults={'selected_option': int(selected)}
                )
                any_answer_saved = True
        if any_answer_saved:
            correct_count = StudentAnswer.objects.filter(student=student, question__exam=exam, selected_option=F('question__correct_option')).count()
            total_questions = questions.count()
            score = (correct_count / total_questions * 20) if total_questions else 0
            Grade.objects.update_or_create(
                student=student,
                exam=exam,
                defaults={'score': score}
            )
            del request.session['student_id']
            return redirect('form:exam_result', exam_id=exam.id, student_id=student.id)

    answers = {a.question_id: a.selected_option for a in StudentAnswer.objects.filter(student=student, question__exam=exam)}
    
    remaining_time = (exam.start_time + timezone.timedelta(minutes=exam.duration) - timezone.now()).total_seconds()
    if remaining_time < 0:
        remaining_time = 0

    return render(request, 'form/Test_Registration.html', {
        'exam': exam,
        'questions': questions,
        'answers': answers,
        'remaining_time': remaining_time,
        'student': student
    })


def exam_result(request, exam_id, student_id):
    """نمایش نتیجه آزمون برای دانش‌آموز"""
    exam = get_object_or_404(Exam, id=exam_id)
    student = get_object_or_404(Student, id=student_id)
    grade = get_object_or_404(Grade, exam=exam, student=student)
    answers = StudentAnswer.objects.filter(student=student, question__exam=exam)
    questions = exam.questions.all()
    total_questions = questions.count()
    correct_count = answers.filter(selected_option=F('question__correct_option')).count()
    wrong_count = total_questions - correct_count
    feedback = []
    for answer in answers:
        question = answer.question
        is_correct = answer.is_correct()
        feedback.append({
            'question': question.text,
            'selected': answer.selected_option,
            'correct': question.correct_option,
            'is_correct': is_correct
        })
    return render(request, 'form/Test_result.html', {
        'exam': exam,
        'student': student,
        'score': grade.score,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'feedback': feedback
    })


@login_required
def exam_grades(request, exam_id):
    """نمایش نمرات آزمون برای معلم"""
    exam = get_object_or_404(Exam, id=exam_id, teacher=request.user)
    grades = Grade.objects.filter(exam=exam).order_by('-score')
    return render(request, 'form/Test_scores.html', {'exam': exam, 'grades': grades})


@login_required
def create_entry_permission(request):
    """صفحه برای ادمین: ایجاد اجازه ورود و ارسال نوتیفیکیشن به معلم"""
    if not request.user.is_superuser:  # فقط برای ادمین (معاونت)
        messages.error(request, 'شما مجاز به دسترسی به این صفحه نیستید.')
        return redirect('form:class_list')

    if request.method == 'POST':
        form = EntryPermissionForm(request.POST)
        if form.is_valid():
            permission = form.save(commit=False)
            permission.created_by = request.user
            permission.save()
            # ایجاد نوتیفیکیشن برای معلم
            message = f"درخواست اجازه ورود برای دانش‌آموز {permission.student} در تاریخ {permission.date} ساعت {permission.time}. دلیل: {permission.reason or 'بدون دلیل'}"
            notification = Notification.objects.create(
                recipient=permission.teacher,
                message=message,
                related_permission=permission
            )
            # ارسال push notification اگر معلم subscribed باشد
            payload = {
                'head': 'نوتیفیکیشن جدید: اجازه ورود',
                'body': message
            }
            send_user_notification(user=permission.teacher, payload=payload, ttl=1000)
            messages.success(request, 'اجازه ورود ایجاد و نوتیفیکیشن به معلم ارسال شد.')
            return redirect('form:create_entry_permission')
    else:
        form = EntryPermissionForm()

    return render(request, 'form/Entry_Permit.html', {'form': form})


@login_required
def notifications(request):
    """پنل نوتیفیکیشن برای کاربر: نمایش و تأیید اجازه ورود"""
    # حذف چک is_staff تا عمومی بشه، اما نوتیف‌های کاربر خودش رو نشون می‌ده
    notifications = Notification.objects.filter(recipient=request.user, is_read=False)
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        action = request.POST.get('action')  # 'approve' یا 'reject'
        try:
            notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
            if notification.related_permission:
                if action == 'approve':
                    notification.related_permission.approved = True
                    notification.related_permission.save()
                    messages.success(request, 'اجازه ورود تأیید شد.')
                elif action == 'reject':
                    notification.related_permission.approved = False
                    notification.related_permission.save()
                    messages.warning(request, 'اجازه ورود رد شد.')
            notification.is_read = True
            notification.save()
        except Exception as e:
            messages.error(request, f'خطا: {str(e)}')
        return redirect('form:notifications')

    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
    vapid_public_key = webpush_settings.get('VAPID_PUBLIC_KEY', '')

    return render(request, 'form/Notif.html', {
        'notifications': notifications,
        'vapid_public_key': vapid_public_key,
        'user_id': request.user.id
    })

def student_register(request):
    tenth = GradeLevel.objects.filter(name='دهم').first()
    if not tenth:
        messages.error(request, "پایه دهم تعریف نشده است. در ادمین اضافه کنید.")
        return redirect('form:class_list')  # یا صفحه دیگر

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            req = form.save(commit=False)
            req.grade_level = tenth
            # parse checkboxها
            req.family_type = ','.join(request.POST.getlist('familyType'))
            req.interests_morning = ','.join([k[7:] for k in request.POST if k.startswith('morning') and request.POST[k] == 'on'])
            req.interests_prayer = ','.join([k[6:] for k in request.POST if k.startswith('prayer') and request.POST[k] == 'on'])
            req.interests_art = ','.join([k[3:] for k in request.POST if k.startswith('art') and request.POST[k] == 'on'])
            req.competitions_quran = ','.join([k[5:] for k in request.POST if k.startswith('quran') and request.POST[k] == 'on'])
            req.competitions_sport = ','.join([k[5:] for k in request.POST if k.startswith('sport') and request.POST[k] == 'on'])
            # خانواده به string
            family_info = f"پدر: {request.POST.get('father_name', '')},{request.POST.get('father_last_name', '')},{request.POST.get('father_national_code', '')},{request.POST.get('father_job', '')},{request.POST.get('father_phone', '')}; مادر: {request.POST.get('mother_name', '')},{request.POST.get('mother_last_name', '')},{request.POST.get('mother_national_code', '')},{request.POST.get('mother_job', '')},{request.POST.get('mother_phone', '')}"
            req.family_info = family_info
            # achievements به string
            achievements = []
            for i in range(1, 3):
                title = request.POST.get(f'achievement_title_{i}', '')
                if title:
                    achievements.append(f"{title},{request.POST.get(f'achievement_rank_{i}', '')},{request.POST.get(f'achievement_level_{i}', '')}")
            req.achievements = '; '.join(achievements)
            req.diseases = request.POST.get('diseases', '')
            req.save()
            # نوتیفیکیشن
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    recipient=admin,
                    message=f"درخواست ثبت نام جدید از {req.first_name} {req.last_name} (پایه دهم، رشته {req.major})"
                )
            messages.success(request, 'درخواست شما ارسال شد و در انتظار تایید است.')
            return redirect('form:student_register')
        else:
            messages.error(request, f'خطا در فرم: {form.errors}')
    else:
        form = StudentRegistrationForm()

    return render(request, 'form/student_register.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Class, Student, ClassSchedule, Attendance, Schedule

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
    return render(request, 'form/login.html')


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

    return render(request, 'form/class_list.html', {
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
            print("POST data:", request.POST)  # دیباگ
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

        return render(request, 'form/attendance.html', {
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
        print("POST data:", request.POST)  # دیباگ
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

                        # حذف رکوردهای غیرتقسیم‌شده قبلی
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

                        # حذف رکوردهای تقسیم‌شده قبلی
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

    return render(request, 'form/weekly_schedule.html', {
        'classes': classes,
        'selected_class': selected_class,
        'schedules': schedules,
        'days': days,
        'zengs': zengs,
        'teachers': User.objects.all()
    })
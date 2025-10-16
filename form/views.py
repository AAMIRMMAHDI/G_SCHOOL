from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import get_user_model  # ✅ استفاده از مدل کاربر سفارشی
from .models import Class, Student, ClassSchedule, Attendance, Schedule

User = get_user_model()  # ✅ مدل کاربر واقعی سیستم (CustomUser) را برمی‌گرداند


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('form:class_list')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'form/login.html')


@login_required
def class_list(request):
    show_all = request.GET.get('show_all', False)
    today = timezone.now().strftime('%a')[:3]
    
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
            )
            | ClassSchedule.objects.filter(teacher=request.user, day=today, schedule__zeng=5)
        )
    
    return render(request, 'form/class_list.html', {
        'class_schedules': class_schedules,
        'show_all': show_all
    })


@login_required
def attendance(request, class_schedule_id):
    class_schedule = get_object_or_404(ClassSchedule, id=class_schedule_id, teacher=request.user)
    
    if not class_schedule.is_active():
        messages.error(request, 'این زنگ تمام شده و نمی‌توانید حضور و غیاب را تغییر دهید.')
        return redirect('form:class_list')
    
    students = Student.objects.filter(class_obj=class_schedule.class_obj)
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status in ['P', 'A', 'L']:
                Attendance.objects.update_or_create(
                    student=student,
                    class_schedule=class_schedule,
                    date=timezone.now().date(),
                    defaults={'status': status}
                )
        messages.success(request, 'حضور و غیاب ثبت شد.')
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


@login_required
def weekly_schedule(request):
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
                    teacher_id = request.POST.get(f'teacher_{day}_{zeng.id}')
                    subject = request.POST.get(f'subject_{day}_{zeng.id}')
                    unit = request.POST.get(f'unit_{day}_{zeng.id}')
                    
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

        messages.success(request, 'برنامه هفتگی با موفقیت ثبت شد.')
        return redirect('form:weekly_schedule')

    if request.GET.get('class_id'):
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

    return render(request, 'form/weekly_schedule.html', {
        'classes': classes,
        'selected_class': selected_class,
        'schedules': schedules,
        'days': days,
        'zengs': zengs,
        'teachers': User.objects.all()  # ✅ حالا با مدل CustomUser کار می‌کند
    })

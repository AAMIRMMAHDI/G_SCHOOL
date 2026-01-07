# admin.py کامل (بدون تغییر، اما برای کامل بودن)
from django.contrib import admin
from django.utils import timezone
from django.urls import path
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Schedule, Class, Student, ClassSchedule, Attendance, Major, GradeLevel, Exam, Question, StudentAnswer, Grade, EntryPermission, Notification, LiveSession  # اضافه شده LiveSession


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_zeng_display', 'start_time', 'end_time')
    list_filter = ('zeng',)
    search_fields = ('zeng',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('row_number', 'first_name', 'last_name', 'father_name', 'class_obj')
    list_filter = ('class_obj',)
    search_fields = ('first_name', 'last_name', 'father_name')


@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ('class_obj', 'schedule', 'teacher', 'get_day_display', 'subject', 'unit', 'is_split', 'split_part')
    list_filter = ('schedule', 'day', 'teacher', 'is_split')
    search_fields = ('class_obj__name', 'teacher__username', 'subject')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('weekly_schedules/', self.admin_site.admin_view(self.weekly_schedules_view), name='weekly_schedules'),
        ]
        return custom_urls + urls

    def weekly_schedules_view(self, request):
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

        try:
            if request.GET.get('class_id'):
                selected_class = get_object_or_404(Class, id=request.GET.get('class_id'))
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
            else:
                messages.info(request, 'لطفاً یک کلاس انتخاب کنید.')
        except Exception as e:
            messages.error(request, f'خطا در بارگذاری برنامه هفتگی: {str(e)}')

        context = {
            'classes': classes,
            'selected_class': selected_class,
            'schedules': schedules,
            'days': days,
            'zengs': zengs,
        }
        return render(request, 'admin/form/classschedule/weekly_schedules.html', context)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_schedule', 'get_status_display', 'date', 'zeng')
    list_filter = ('status', 'date', 'class_schedule__schedule')
    search_fields = ('student__first_name', 'student__last_name')

    def zeng(self, obj):
        return obj.class_schedule.schedule.get_zeng_display()
    zeng.short_description = 'زنگ'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.path == '/admin/form/attendance/absent/':
            return qs.filter(status='A')
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.path == '/admin/form/attendance/absent/':
            self.list_display = ('student', 'class_schedule', 'date', 'zeng')
            self.list_filter = ('date', 'class_schedule__schedule')
            try:
                current_month = timezone.now().month
                absent_counts = Attendance.objects.filter(
                    status='A',
                    date__month=current_month
                ).values('student__first_name', 'student__last_name').annotate(count=Count('id'))
                extra_context['absent_counts'] = absent_counts
            except Exception as e:
                messages.error(request, f'خطا در بارگذاری آمار غیبت‌ها: {str(e)}')
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('absent/', self.admin_site.admin_view(self.absent_view), name='absent_list'),
        ]
        return custom_urls + urls

    def absent_view(self, request):
        return HttpResponseRedirect('/admin/form/attendance/absent/')


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'class_obj', 'major', 'grade_level', 'duration', 'start_time')
    list_filter = ('teacher', 'major', 'grade_level')
    search_fields = ('title', 'teacher__username')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'text', 'correct_option')
    list_filter = ('exam',)
    search_fields = ('text',)


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'selected_option', 'submitted_at')
    list_filter = ('question__exam',)
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'calculated_at')
    list_filter = ('exam',)
    search_fields = ('student__first_name', 'student__last_name')


@admin.register(EntryPermission)
class EntryPermissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'teacher', 'date', 'time', 'approved')
    list_filter = ('approved', 'date')
    search_fields = ('student__first_name', 'student__last_name', 'teacher__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'message')

@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'class_schedule', 'start_time', 'is_active', 'room_name')
    list_filter = ('is_active', 'teacher')
    search_fields = ('title', 'room_name')
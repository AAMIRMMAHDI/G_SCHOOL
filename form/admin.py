# admin.py کامل اصلاح‌شده (fields آپدیت برای TextField، بدون نیاز به JSON)
from django.contrib import admin
from django.utils import timezone
from django.urls import path
from django.http import HttpResponseRedirect
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Schedule, Class, Student, ClassSchedule, Attendance, Major, GradeLevel, Exam, Question, StudentAnswer, Grade, EntryPermission, Notification, StudentRegistrationRequest


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_zeng_display', 'start_time', 'end_time')
    list_filter = ('zeng',)
    search_fields = ('zeng',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'major', 'grade_level')
    search_fields = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('row_number', 'first_name', 'last_name', 'father_name', 'class_obj')
    list_filter = ('class_obj',)
    search_fields = ('first_name', 'last_name', 'father_name')



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


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'score', 'calculated_at')
    list_filter = ('exam',)
    search_fields = ('student__first_name', 'student__last_name')

@admin.register(StudentRegistrationRequest)
class StudentRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'major', 'grade_level', 'status', 'created_at')
    list_filter = ('status', 'major', 'grade_level')
    search_fields = ('first_name', 'last_name')
    fields = ('first_name', 'last_name', 'nickname', 'father_name', 'birth_day', 'birth_month', 'birth_year', 
              'national_code', 'family_type', 'children_count', 'boys_count', 'girls_count', 'child_order',
              'family_info', 'province', 'county', 'city', 'postal_code', 'home_phone', 'father_education',
              'mother_education', 'father_phone', 'mother_phone', 'address', 'interests_morning', 'interests_prayer',
              'interests_art', 'competitions_quran', 'competitions_sport', 'achievements', 'other_skills',
              'diseases', 'major', 'grade_level', 'report_card_image', 'class_assigned', 'status', 'notes')
    actions = ['approve_request', 'reject_request']

    def approve_request(self, request, queryset):
        tenth = GradeLevel.objects.filter(name='دهم').first()
        if not tenth:
            self.message_user(request, "پایه دهم تعریف نشده.", level=messages.ERROR)
            return
        for req in queryset:
            if req.status != 'P':
                self.message_user(request, f"فقط درخواست‌های pending قابل تایید است: {req}", level=messages.ERROR)
                continue
            if not req.grade_level:
                req.grade_level = tenth
                req.save()
            if req.grade_level != tenth:
                self.message_user(request, f"فقط پایه دهم مجاز است: {req}", level=messages.ERROR)
                continue
            if not req.class_assigned:
                self.message_user(request, f"کلاس را برای {req} انتخاب کنید.", level=messages.ERROR)
                continue
            if not req.class_assigned.has_capacity():
                self.message_user(request, f"کلاس {req.class_assigned} ظرفیت ندارد.", level=messages.ERROR)
                continue
            if req.class_assigned.grade_level != req.grade_level or req.class_assigned.major != req.major:
                self.message_user(request, f"کلاس {req.class_assigned} با پایه یا رشته مطابقت ندارد.", level=messages.ERROR)
                continue
            student = Student.objects.create(
                class_obj=req.class_assigned,
                row_number=req.class_assigned.students.count() + 1,
                first_name=req.first_name,
                last_name=req.last_name,
                father_name=req.father_name
            )
            req.status = 'A'
            req.save()
            self.message_user(request, f"درخواست {req} تایید شد و دانش‌آموز {student} اضافه شد.", level=messages.SUCCESS)

    def reject_request(self, request, queryset):
        for req in queryset:
            if req.status == 'P':
                req.status = 'R'
                req.save()
                self.message_user(request, f"درخواست {req} رد شد.", level=messages.WARNING)
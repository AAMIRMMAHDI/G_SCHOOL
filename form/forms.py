# forms.py کامل
from django import forms
from django.contrib.auth import get_user_model
from .models import Exam, Major, GradeLevel, Class, EntryPermission, Student, ClassSchedule

User = get_user_model()

class ExamForm(forms.ModelForm):
    major = forms.ModelChoiceField(queryset=Major.objects.all(), label="رشته")
    grade_level = forms.ModelChoiceField(queryset=GradeLevel.objects.all(), label="پایه تحصیلی")
    class_obj = forms.ModelChoiceField(queryset=Class.objects.all(), label="کلاس")

    class Meta:
        model = Exam
        fields = ['title', 'class_obj', 'major', 'grade_level', 'duration', 'start_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class EntryPermissionForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all().order_by('class_obj__name', 'row_number'), label="نام دانش‌آموز")
    teacher = forms.ModelChoiceField(
        queryset=User.objects.filter(class_schedules__isnull=False).distinct().order_by('username'),
        label="نام معلم"  # حالا همه معلم‌هایی که کلاس دارند ظاهر می‌شن
    )

    class Meta:
        model = EntryPermission
        fields = ['student', 'teacher', 'reason', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
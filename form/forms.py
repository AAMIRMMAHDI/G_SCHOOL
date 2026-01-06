# forms.py کامل
from django import forms
from .models import Exam, Major, GradeLevel, Class

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
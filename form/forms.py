# forms.py کامل اصلاح‌شده (fields آپدیت برای TextField)
from django import forms
from django.contrib.auth import get_user_model
from .models import Exam, Major, GradeLevel, Class, EntryPermission, Student, ClassSchedule, StudentRegistrationRequest

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

class StudentRegistrationForm(forms.ModelForm):
    # فیلدهای checkbox رو به عنوان CharField هندل می‌کنیم (در ویو parse می‌شه)
    family_type = forms.CharField(widget=forms.HiddenInput, required=False)
    interests_morning = forms.CharField(widget=forms.HiddenInput, required=False)
    interests_prayer = forms.CharField(widget=forms.HiddenInput, required=False)
    interests_art = forms.CharField(widget=forms.HiddenInput, required=False)
    competitions_quran = forms.CharField(widget=forms.HiddenInput, required=False)
    competitions_sport = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = StudentRegistrationRequest
        fields = [
            'first_name', 'last_name', 'nickname', 'father_name',
            'birth_day', 'birth_month', 'birth_year', 'national_code',
            'family_type', 'children_count', 'boys_count', 'girls_count', 'child_order',
            'province', 'county', 'city', 'postal_code',
            'home_phone', 'father_education', 'mother_education', 'father_phone', 'mother_phone', 'address',
            'interests_morning', 'interests_prayer', 'interests_art',
            'competitions_quran', 'competitions_sport',
            'other_skills', 'diseases', 'major', 'report_card_image', 'grade_level'
        ]
        widgets = {
            'birth_day': forms.NumberInput(attrs={'placeholder': 'روز', 'style': 'width: 70px;'}),
            'birth_month': forms.NumberInput(attrs={'placeholder': 'ماه', 'style': 'width: 70px;'}),
            'birth_year': forms.NumberInput(attrs={'placeholder': 'سال', 'style': 'width: 100px;'}),
            'major': forms.Select(attrs={'class': 'form-select'}),
            'report_card_image': forms.FileInput(attrs={'accept': 'image/*'}),
            'grade_level': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenth = GradeLevel.objects.filter(name='دهم').first()
        if tenth:
            self.fields['grade_level'].initial = tenth
            self.fields['grade_level'].queryset = GradeLevel.objects.filter(pk=tenth.pk)
        else:
            self.fields['grade_level'].widget = forms.Select(queryset=GradeLevel.objects.none())
            self.add_error(None, "پایه دهم تعریف نشده.")

    def clean_grade_level(self):
        grade = self.cleaned_data.get('grade_level')
        tenth = GradeLevel.objects.filter(name='دهم').first()
        if not tenth:
            raise forms.ValidationError("پایه دهم تعریف نشده. در ادمین اضافه کنید.")
        if grade and grade != tenth:
            raise forms.ValidationError("فقط پایه دهم مجاز است.")
        return tenth
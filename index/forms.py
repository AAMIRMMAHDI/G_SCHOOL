from django import forms
from .models import ContactMessage, EducationalResource, Major


# ---------- فرم پیام تماس ----------
class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'نام و نام خانوادگی خود را وارد کنید'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'example@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '09xxxxxxxxx'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'موضوع پیام خود را وارد کنید'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'متن پیام خود را بنویسید...'
            }),
        }


# ---------- فرم فیلتر منابع آموزشی ----------
class ResourceFilterForm(forms.Form):
    major = forms.ChoiceField(
        choices=[('all', 'همه رشته‌ها')],
        required=False,
        label='رشته تحصیلی'
    )
    
    grade = forms.ChoiceField(
        choices=[
            ('all', 'همه پایه‌ها'),
            (10, 'پایه دهم'),
            (11, 'پایه یازدهم'),
            (12, 'پایه دوازدهم'),
        ],
        required=False,
        label='پایه تحصیلی'
    )
    
    search = forms.CharField(
        required=False,
        label='جستجو',
        widget=forms.TextInput(attrs={'placeholder': 'جستجو در منابع...'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # بارگذاری رشته‌ها از دیتابیس
        major_choices = [('all', 'همه رشته‌ها')] + [(major.id, major.title) for major in Major.objects.all()]
        self.fields['major'].choices = major_choices

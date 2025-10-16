from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Blog, BlogImage, BlogComment, Category

class BlogRegisterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].label_from_instance = lambda obj: obj.name

    class Meta:
        model = Blog
        fields = ['title', 'category', 'content', 'address', 'city', 'district']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('مثال: معرفی هنرستان')}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': _('در مورد وبلاگ توضیح دهید...')}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('آدرس کامل')}),
            'city': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('اراک', 'اراک'),
            ]),
            'district': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('منطقه یا محله')}),
        }
        labels = {
            'title': _('عنوان وبلاگ'),
            'category': _('دسته‌بندی'),
            'content': _('محتوا'),
            'address': _('آدرس'),
            'city': _('شهر'),
            'district': _('منطقه'),
        }

class BlogImageForm(forms.ModelForm):
    class Meta:
        model = BlogImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'}),  # multiple رو حذف کردیم
        }

class BlogCommentForm(forms.ModelForm):
    RATING_CHOICES = [
        (1, '۱ ستاره'),
        (2, '۲ ستاره'),
        (3, '۳ ستاره'),
        (4, '۴ ستاره'),
        (5, '۵ ستاره'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        label=_('امتیاز')
    )
    
    class Meta:
        model = BlogComment
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea', 
                'placeholder': _('نظر خود را بنویسید...'),
                'rows': 5
            }),
        }
        labels = {
            'comment': _('نظر'),
        }
    
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        return float(rating)
    




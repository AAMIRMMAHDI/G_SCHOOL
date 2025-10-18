from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'form'

urlpatterns = [
    # URL برای ورود کاربر
    path('login/', views.user_login, name='login'),
    # URL برای نمایش لیست کلاس‌ها
    path('classes/', views.class_list, name='class_list'),
    # URL برای ثبت حضور و غیاب یک کلاس
    path('class_schedule/<int:class_schedule_id>/attendance/', views.attendance, name='attendance'),
    # URL برای مدیریت برنامه هفتگی
    path('weekly_schedule/', views.weekly_schedule, name='weekly_schedule'),
    # URL برای خروج از سیستم
    path('logout/', LogoutView.as_view(next_page='form:login'), name='logout'),
]
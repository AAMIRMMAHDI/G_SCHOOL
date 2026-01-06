# urls.py کامل
from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'form'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('classes/', views.class_list, name='class_list'),
    path('class_schedule/<int:class_schedule_id>/attendance/', views.attendance, name='attendance'),
    path('weekly_schedule/', views.weekly_schedule, name='weekly_schedule'),
    path('logout/', LogoutView.as_view(next_page='form:login'), name='logout'),
    path('create_exam/', views.create_exam, name='create_exam'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/grades/', views.exam_grades, name='exam_grades'),
    path('exam/<int:exam_id>/result/<int:student_id>/', views.exam_result, name='exam_result'),
    path('entry_permission/create/', views.create_entry_permission, name='create_entry_permission'),
    path('notifications/', views.notifications, name='notifications'),
    path('webpush/', include('webpush.urls')),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript'), name='sw.js'),
]
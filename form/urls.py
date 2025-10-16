from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'form'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('classes/', views.class_list, name='class_list'),
    path('class_schedule/<int:class_schedule_id>/attendance/', views.attendance, name='attendance'),
    path('weekly_schedule/', views.weekly_schedule, name='weekly_schedule'),
    path('logout/', LogoutView.as_view(next_page='form:login'), name='logout'),
]
from django.urls import path
from . import views

app_name = 'root'  # بسیار مهم برای reverse و نامگذاری مسیرها

urlpatterns = [
    # ---------- صفحه درباره ما ----------
    path('about/', views.about_view, name='about'),

    # ---------- صفحه تماس ----------
    path('contact/', views.contact_view, name='contact'),

    # ---------- لیست رشته‌ها ----------
    path('majors/', views.majors, name='majors'),
    path('majors/<int:major_id>/', views.major_detail, name='major_detail'),

    # ---------- منابع آموزشی ----------
    path('resources/', views.resources_list, name='resources_list'),
    path('resources/download/<int:resource_id>/', views.download_resource, name='download_resource'),
    path('resources/view/<int:resource_id>/', views.view_resource, name='view_resource'),

    # ---------- API منابع آموزشی ----------
    path('api/resources/', views.api_resources, name='api_resources'),
]

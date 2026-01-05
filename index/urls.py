from django.urls import path
from . import views

app_name = 'root'  

urlpatterns = [
    # ---------- لیست رشته‌ها ----------
    path('majors/', views.majors, name='majors'),
    path('majors/<int:major_id>/', views.major_detail, name='major_detail'),

    # ---------- منابع آموزشی ----------
    path('resources/', views.resources_list, name='resources_list'),
    path('resources/download/<int:resource_id>/', views.download_resource, name='download_resource'),
    path('resources/view/<int:resource_id>/', views.view_resource, name='view_resource'),

    # ---------- API منابع آموزشی ----------
    path('api/resources/', views.api_resources, name='api_resources'),



    path('', views.send_list_view, name='send_list'),
    path('set/', views.send_register_view, name='send_register'),
    path('blog/<str:slug>/', views.send_detail_view, name='send_detail'),
    path('blog/<str:slug>/comment/', views.add_comment_view, name='add_comment'),

]

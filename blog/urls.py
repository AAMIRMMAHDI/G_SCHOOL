from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('list/', views.send_list_view, name='send_list'),
    path('set/', views.send_register_view, name='send_register'),
    path('blog/<str:slug>/', views.send_detail_view, name='send_detail'),
    path('blog/<str:slug>/comment/', views.add_comment_view, name='add_comment'),

]
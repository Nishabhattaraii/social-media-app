from django.conf import settings
from django.urls import path
from student import views

urlpatterns = [
    path('register/', views.register, name="register"),
    path('', views.login, name="login"),
    path('post_create/', views.post_create, name="post_create"),
    path('post_list/',views.post_list, name="post_list"),
    path('<int:post_id>/delete/',views.post_delete, name="post_delete"),
    path('<int:post_id>/edit/',views.post_edit, name='post_edit'),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('logout/', views.logout_view, name='logout'),
]

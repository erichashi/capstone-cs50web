
from django.urls import path


from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('setup', views.setup, name='setup'),

    path('post/<int:post_id>', views.post_view, name='post_view'),
    
    path('edit/post/<int:post_id>', views.post_edit, name='post_edit'),
    path('delete/post/<int:post_id>', views.post_delete, name='post_delete'),
    
    path('follow/<int:user_id>', views.follow, name='follow'),

    path('subject/<str:subject>', views.subject_view, name='subject'),
    
    path('feed', views.feed, name='feed'),

    path('saved', views.saved, name='saved'),
    path('save/<int:post_id>', views.save_post, name='save_post'),

    #------
    path("compose", views.compose, name="compose"),
    path("<str:username>", views.profile, name="profile"),
    
]



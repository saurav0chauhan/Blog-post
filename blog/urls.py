from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-blog/', views.create_blog, name='create_blog'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:blog_id>/edit/', views.edit_blog, name='edit_blog'),
    path('blog/<int:blog_id>/delete/', views.delete_blog, name='delete_blog'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('blog/<int:blog_id>/like/', views.toggle_like, name='toggle_like'),
    path('search/', views.search, name='search'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
]

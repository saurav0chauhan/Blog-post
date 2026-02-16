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
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('blog/<int:blog_id>/like/', views.toggle_like, name='toggle_like'),
    path('search/', views.search, name='search'),
    path('profile/<int:user_id>/', views.profile, name='profile'),
    
    # SuperAdmin routes
    path('superadmin/register/', views.superadmin_register, name='superadmin_register'),
    path('superadmin/login/', views.superadmin_login, name='superadmin_login'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('superadmin/create/', views.superadmin_create, name='superadmin_create'),
    path('superadmin/logout/', views.superadmin_logout, name='superadmin_logout'),
    path('superadmin/deactivate/<int:admin_id>/', views.superadmin_deactivate, name='superadmin_deactivate'),
]

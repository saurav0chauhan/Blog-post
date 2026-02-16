from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import RegistrationForm, LoginForm
from .models import Blog, Tag, Comment, Like, Permission
import json
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt


def home(request):
    """Home page - display blogs"""
    blogs = Blog.objects.filter(status='published').order_by('-published_at')
    context = {
        'blogs': blogs,
    }
    return render(request, 'home.html', context)


@require_http_methods(["GET", "POST"])
def register(request):
    """Registration page"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    context = {
        'form': form,
        'page_title': 'Register'
    }
    return render(request, 'register.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'page_title': 'Login'
    }
    return render(request, 'login.html', context)


@login_required(login_url='login')
def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required(login_url='login')
@require_http_methods(["POST"])
def toggle_like(request, blog_id):
    """Toggle like/unlike for a blog post"""
    from .models import Blog, Like

    try:
        # allow the author to view their own post even if not published
        blog = Blog.objects.get(id=blog_id)
        if blog.status != 'published':
            if not (request.user.is_authenticated and blog.author == request.user):
                raise Blog.DoesNotExist
    except Blog.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('home')

    like_qs = Like.objects.filter(blog=blog, user=request.user)
    if like_qs.exists():
        like_qs.delete()
        messages.info(request, 'You unliked this post.')
    else:
        Like.objects.create(blog=blog, user=request.user, tenant_id=1)
        messages.success(request, 'You liked this post.')

    return redirect('blog_detail', blog_id=blog_id)


def search(request):
    """Search blogs and user accounts by name or content"""
    q = request.GET.get('q', '').strip()
    blogs = []
    users = []
    if q:
        blogs = Blog.objects.filter(title__icontains=q) | Blog.objects.filter(content__icontains=q)
        users = Tag.objects.none()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(name__icontains=q) | User.objects.filter(email__icontains=q)

    context = {
        'query': q,
        'blogs': blogs.distinct(),
        'users': users.distinct(),
        'page_title': f"Search results for '{q}'"
    }
    return render(request, 'search_results.html', context)


def profile(request, user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        profile_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')

    published_blogs = profile_user.blogs.filter(status='published').order_by('-published_at')
    context = {
        'profile_user': profile_user,
        'published_blogs': published_blogs,
        'page_title': f"{profile_user.name} - Profile"
    }
    return render(request, 'profile.html', context)


@login_required(login_url='login')
def dashboard(request):
    """User dashboard"""
    user_blogs = request.user.blogs.all().order_by('-created_at')
    # categories with post counts for the dashboard
    from .models import Category
    categories = Category.objects.annotate(post_count=Count('blogs')).order_by('-post_count')[:12]
    context = {
        'user_blogs': user_blogs,
        'categories': categories,
        'page_title': 'Dashboard'
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def create_blog(request):
    """Create a new blog post"""
    # Only users with writer role can create blogs
    try:
        if not request.user.user_roles.filter(name='writer').exists():
            messages.error(request, 'You do not have permission to write blog posts. Register as a writer to create posts.')
            return redirect('dashboard')
    except Exception:
        pass
    if request.method == 'POST':
        from .models import Blog, Category
        
        title = request.POST.get('title')
        excerpt = request.POST.get('excerpt')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        featured = request.FILES.get('featured_image')
        
        try:
            category = Category.objects.get(id=category_id) if category_id else None
        except Category.DoesNotExist:
            category = None
        
        blog = Blog.objects.create(
            title=title,
            excerpt=excerpt,
            content=content,
            category=category,
            featured_image=featured,
            author=request.user,
            tenant_id=1,
            status='draft'
        )
        # handle tags (comma separated)
        tags_input = request.POST.get('tags', '')
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tn in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tenant_id=1, name=tn)
                blog.tags.add(tag_obj)
        messages.success(request, 'Blog post created successfully!')
        return redirect('dashboard')
    
    from .models import Category
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'page_title': 'Create Blog'
    }
    return render(request, 'create_blog.html', context)


@login_required(login_url='login')
def edit_blog(request, blog_id):
    """Edit a blog post"""
    from .models import Blog, Category
    
    try:
        blog = Blog.objects.get(id=blog_id, author=request.user)
    except Blog.DoesNotExist:
        messages.error(request, 'Blog post not found or you do not have permission to edit it.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.excerpt = request.POST.get('excerpt')
        blog.content = request.POST.get('content')
        # replace featured image if provided
        featured = request.FILES.get('featured_image')
        if featured:
            blog.featured_image = featured

        # remove featured image
        remove_image = request.POST.get('remove_image') in ['1', 'true', 'on']
        if remove_image and blog.featured_image:
            try:
                blog.featured_image.delete(save=False)
            except Exception:
                pass
            blog.featured_image = None
        
        category_id = request.POST.get('category')
        if category_id:
            try:
                blog.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        # handle tags (replace existing)
        tags_input = request.POST.get('tags', '')
        blog.save()
        if tags_input is not None:
            blog.tags.clear()
            tag_names = [t.strip() for t in tags_input.split(',') if t.strip()]
            for tn in tag_names:
                tag_obj, _ = Tag.objects.get_or_create(tenant_id=1, name=tn)
                blog.tags.add(tag_obj)
        messages.success(request, 'Blog post updated successfully!')
        return redirect('dashboard')
    
    categories = Category.objects.all()
    context = {
        'blog': blog,
        'categories': categories,
        'page_title': 'Edit Blog'
    }
    return render(request, 'edit_blog.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_blog(request, blog_id):
    """Delete a blog post (POST only)"""
    from .models import Blog

    try:
        blog = Blog.objects.get(id=blog_id, author=request.user)
        blog.delete()
        messages.success(request, 'Blog post deleted successfully!')
    except Blog.DoesNotExist:
        messages.error(request, 'Blog post not found or you do not have permission to delete it.')

    return redirect('dashboard')


@login_required(login_url='login')
@require_http_methods(["POST"])
def delete_account(request):
    """Delete the currently logged-in user's account (POST only)."""
    user = request.user
    logout(request)
    try:
        user.delete()
        messages.success(request, 'Your account has been deleted.')
    except Exception:
        messages.error(request, 'There was an error deleting your account.')
    return redirect('home')


def blog_detail(request, blog_id):
    """Display a single blog post"""
    from .models import Blog, Comment
    
    try:
        blog = Blog.objects.get(id=blog_id, status='published')
    except Blog.DoesNotExist:
        messages.error(request, 'Blog post not found.')
        return redirect('home')
    
    # separate image comments and regular comments
    image_comments_qs = blog.comments.filter(status='approved', is_image=True).order_by('-created_at')
    comments = blog.comments.filter(status='approved', is_image=False).order_by('-created_at')

    # prepare image comments list for inline images (comments may reference image_url)
    image_comments = list(image_comments_qs.values('id', 'name', 'comment', 'image_url', 'created_at'))
    
    # likes info
    likes_count = blog.likes.count()
    user_liked = False
    if request.user.is_authenticated:
        user_liked = blog.likes.filter(user=request.user).exists()

    context = {
        'blog': blog,
        'comments': comments,
        'image_comments': image_comments_qs,
        'image_comments_json': json.dumps(image_comments, default=str),
        'likes_count': likes_count,
        'user_liked': user_liked,
        'page_title': blog.title
    }
    return render(request, 'blog_detail.html', context)


def add_comment(request, blog_id):
    """Add a comment to a blog post"""
    if request.method == 'POST':
        from .models import Blog, Comment
        
        try:
            blog = Blog.objects.get(id=blog_id, status='published')
        except Blog.DoesNotExist:
            messages.error(request, 'Blog post not found.')
            return redirect('home')
        # determine if this is an image comment
        is_image = request.POST.get('is_image') in ['1', 'true', 'on']

        # permission check: only allow commenting if user has 'can_comment' permission
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to post comments.')
            return redirect('login')

        has_perm = Permission.objects.filter(roles__users=request.user, name='can_comment').exists()
        if not has_perm:
            messages.error(request, 'You do not have permission to comment.')
            return redirect('blog_detail', blog_id=blog_id)

        # use authenticated user's name/email
        user = request.user
        name = user.name
        email = user.email

        comment_text = request.POST.get('comment')
        image_file = request.FILES.get('image')
        image_url = request.POST.get('image_url') or None

        # if image_url is provided, treat as image comment
        if image_url:
            is_image = True

        Comment.objects.create(
            blog=blog,
            user=user,
            name=name,
            email=email,
            is_image=is_image,
            image=image_file,
            image_url=image_url,
            comment=comment_text,
            tenant_id=1,
            status='pending'
        )
        messages.success(request, 'Your comment has been submitted and is pending approval.')
        return redirect('blog_detail', blog_id=blog_id)
    
    return redirect('home')

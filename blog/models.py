from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.text import slugify


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email

    @property
    def is_writer(self):
        try:
            return self.user_roles.filter(name='writer').exists()
        except Exception:
            return False

    @property
    def is_reader(self):
        try:
            return self.user_roles.filter(name='reader').exists()
        except Exception:
            return False


class SuperAdminType(models.Model):
    """SuperAdmin role/type options"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    permissions_level = models.IntegerField(default=1, help_text="Higher number = more permissions")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'superadmin_types'
        verbose_name = 'SuperAdmin Type'
        verbose_name_plural = 'SuperAdmin Types'
        ordering = ['permissions_level']
    
    def __str__(self):
        return self.name


class SuperAdmin(models.Model):
    """Separate SuperAdmin model with independent auth"""
    
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    admin_type = models.ForeignKey(SuperAdminType, on_delete=models.SET_NULL, null=True, related_name='superadmins')
    password_hash = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to='superadmin/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'superadmins'
        verbose_name = 'SuperAdmin'
        verbose_name_plural = 'SuperAdmins'
    
    def __str__(self):
        return f"SuperAdmin: {self.email}"


class Role(models.Model):
    """User roles"""
    
    name = models.CharField(max_length=50, unique=True)
    users = models.ManyToManyField(User, through='UserRole', related_name='user_roles')
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name


class Permission(models.Model):
    """Permissions for roles"""
    
    name = models.CharField(max_length=100, unique=True)
    roles = models.ManyToManyField(Role, through='RolePermission', related_name='role_permissions')
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Many-to-many relationship between roles and permissions"""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = ('role', 'permission')
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(models.Model):
    """Many-to-many relationship between users and roles"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class Category(models.Model):
    """Blog categories"""
    
    tenant_id = models.IntegerField()
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    
    class Meta:
        db_table = 'categories'
        unique_together = ('tenant_id', 'slug')
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='categories_index_0'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Blog tags"""
    
    tenant_id = models.IntegerField()
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    
    class Meta:
        db_table = 'tags'
        unique_together = ('tenant_id', 'slug')
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='tags_index_1'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Blog(models.Model):
    """Blog posts"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    tenant_id = models.IntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    tags = models.ManyToManyField('Tag', related_name='blogs', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blogs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='blogs')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blogs'
        unique_together = ('tenant_id', 'slug')
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='blogs_index_2'),
            models.Index(fields=['tenant_id', 'status'], name='idx_blogs_tenant_status'),
            models.Index(fields=['tenant_id', 'slug'], name='idx_blogs_slug'),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Ensure title is not empty
        if not self.title:
            raise ValueError('Blog title is required')
        
        # Generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Ensure slug is not empty
        if not self.slug:
            self.slug = f"blog-{timezone.now().timestamp()}"
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        # Clear published_at if status changes away from published
        if self.status != 'published' and self.published_at:
            self.published_at = None
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """Blog comments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
        ('rejected', 'Rejected'),
    ]
    
    tenant_id = models.IntegerField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    is_image = models.BooleanField(default=False)
    image = models.ImageField(upload_to='comments/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"


class Like(models.Model):
    """User likes for blog posts"""

    tenant_id = models.IntegerField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'likes'
        unique_together = ('tenant_id', 'blog', 'user')

    def __str__(self):
        return f"{self.user.email} likes {self.blog.title}"
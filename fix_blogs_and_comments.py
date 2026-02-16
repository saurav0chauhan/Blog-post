#!/usr/bin/env python
"""
Script to fix blog and comment issues in the database:
1. Ensure all blogs have valid slugs
2. Ensure published blogs have published_at set
3. Fix any empty titles
4. Approve pending comments
"""

import os
import django
from django.utils.text import slugify
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Blog, Comment

def fix_blogs():
    """Fix blog-related issues"""
    print("\n=== Fixing Blogs ===")
    
    # Get all blogs
    blogs = Blog.objects.all()
    fixed_count = 0
    
    for blog in blogs:
        changes = False
        
        # Fix empty title
        if not blog.title or blog.title.strip() == '':
            print(f"  ⚠️  Blog ID {blog.id} has empty title - fixing")
            blog.title = f"Untitled Blog {blog.id}"
            changes = True
        
        # Fix missing or invalid slug
        if not blog.slug or blog.slug.strip() == '':
            new_slug = slugify(blog.title)
            if not new_slug:
                new_slug = f"blog-{blog.id}"
            print(f"  ✓ Blog ID {blog.id} - generating slug: {new_slug}")
            blog.slug = new_slug
            changes = True
        
        # Fix published blogs without published_at
        if blog.status == 'published' and not blog.published_at:
            print(f"  ✓ Blog ID {blog.id} - setting published_at to now")
            blog.published_at = timezone.now()
            changes = True
        
        # Clear published_at for non-published blogs
        if blog.status != 'published' and blog.published_at:
            print(f"  ✓ Blog ID {blog.id} - clearing published_at (status: {blog.status})")
            blog.published_at = None
            changes = True
        
        if changes:
            try:
                blog.save()
                fixed_count += 1
                print(f"  ✅ Blog ID {blog.id} - saved successfully")
            except Exception as e:
                print(f"  ❌ Error saving Blog ID {blog.id}: {e}")
    
    print(f"\n✅ Fixed {fixed_count} blogs")
    print(f"📊 Total blogs in database: {blogs.count()}")

def fix_comments():
    """Fix comment-related issues"""
    print("\n=== Fixing Comments ===")
    
    # Get pending comments
    pending_comments = Comment.objects.filter(status='pending')
    approved_count = 0
    
    if pending_comments.count() > 0:
        print(f"Found {pending_comments.count()} pending comments")
        
        for comment in pending_comments:
            print(f"  ✓ Comment ID {comment.id} - approving")
            comment.status = 'approved'
            try:
                comment.save()
                approved_count += 1
            except Exception as e:
                print(f"  ❌ Error saving Comment ID {comment.id}: {e}")
    else:
        print("No pending comments found")
    
    print(f"\n✅ Approved {approved_count} pending comments")
    
    # Show comment statistics
    total_comments = Comment.objects.count()
    approved = Comment.objects.filter(status='approved').count()
    rejected = Comment.objects.filter(status='rejected').count()
    spam = Comment.objects.filter(status='spam').count()
    
    print(f"\n📊 Comment Statistics:")
    print(f"  Total: {total_comments}")
    print(f"  Approved: {approved}")
    print(f"  Rejected: {rejected}")
    print(f"  Spam: {spam}")

def verify_data():
    """Verify data integrity"""
    print("\n=== Verifying Data Integrity ===")
    
    # Check for blogs with invalid slugs
    blogs_without_slug = Blog.objects.filter(slug__exact='').count()
    if blogs_without_slug > 0:
        print(f"  ⚠️  Found {blogs_without_slug} blogs without slugs")
    else:
        print(f"  ✅ All blogs have valid slugs")
    
    # Check for blogs without titles
    blogs_without_title = Blog.objects.filter(title__exact='').count()
    if blogs_without_title > 0:
        print(f"  ⚠️  Found {blogs_without_title} blogs without titles")
    else:
        print(f"  ✅ All blogs have titles")
    
    # Check for published blogs without published_at
    published_no_date = Blog.objects.filter(status='published', published_at__isnull=True).count()
    if published_no_date > 0:
        print(f"  ⚠️  Found {published_no_date} published blogs without published_at")
    else:
        print(f"  ✅ All published blogs have published_at")
    
    # Check for comments without blog
    orphaned_comments = Comment.objects.filter(blog__isnull=True).count()
    if orphaned_comments > 0:
        print(f"  ⚠️  Found {orphaned_comments} orphaned comments")
    else:
        print(f"  ✅ No orphaned comments")

if __name__ == '__main__':
    print("Starting blog and comment maintenance script...")
    
    try:
        verify_data()
        fix_blogs()
        fix_comments()
        verify_data()
        
        print("\n" + "="*50)
        print("✅ Maintenance complete!")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Error during maintenance: {e}")
        import traceback
        traceback.print_exc()

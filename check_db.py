#!/usr/bin/env python
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from blog.models import User, Blog, Comment, Category, Tag

print("=" * 60)
print("SQLite DATABASE CONNECTION VERIFIED")
print("=" * 60)

# Get database info
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print(f"\nDatabase: SQLite (db.sqlite3)")
print(f"Location: db.sqlite3")
print(f"Tables in database: {len(tables)} tables")

# Count users
user_count = User.objects.count()
print(f"\n{'='*60}")
print(f"REGISTERED USERS: {user_count}")
print(f"{'='*60}")
if user_count > 0:
    users = User.objects.all().values('id', 'name', 'email', 'created_at', 'is_active')
    for user in users:
        print(f"  ID: {user['id']}")
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  Joined: {user['created_at']}")
        print(f"  Active: {user['is_active']}")
        print()

# Count blog posts
print(f"{'='*60}")
blog_count = Blog.objects.count()
print(f"BLOG POSTS: {blog_count}")
print(f"{'='*60}")
if blog_count > 0:
    blogs = Blog.objects.all().values('id', 'title', 'author__email', 'status', 'created_at')
    for blog in blogs:
        print(f"  ID: {blog['id']}")
        print(f"  Title: {blog['title']}")
        print(f"  Author: {blog['author__email']}")
        print(f"  Status: {blog['status']}")
        print(f"  Created: {blog['created_at']}")
        print()

# Count comments
print(f"{'='*60}")
comment_count = Comment.objects.count()
print(f"COMMENTS: {comment_count}")
print(f"{'='*60}")

print(f"Categories: {Category.objects.count()}")
print(f"Tags: {Tag.objects.count()}")

print("\n" + "=" * 60)
print("CONNECTION SUCCESSFUL - Using SQLite Database")
print("=" * 60)

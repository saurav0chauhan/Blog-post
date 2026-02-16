#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Category

categories = [
    'Daily Life',
    'Motivation',
    'Self Improvement',
    'Career Guidance',
    'Student Life',
    'AI & Machine Learning',
    'Startups',
    'Freelancing',
    'Online Earning',
    'Tech News',
    'Technology',
    'Programming',
    'Django',
    'Projects',
    'Tutorials',
    'Tips & Tricks',
]

for name in categories:
    obj, created = Category.objects.get_or_create(name=name, tenant_id=1)
    if created:
        print(f"Created category: {name}")
    else:
        print(f"Already exists: {name}")

print("Done.")

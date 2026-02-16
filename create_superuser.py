#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import User

# Check if superuser already exists
if User.objects.filter(email='admin@localhost.com').exists():
    print("✅ Superuser already exists: admin@localhost.com")
else:
    # Create a new superuser
    admin_user = User.objects.create_superuser(
        email='admin@localhost.com',
        name='Admin',
        password='admin@123'
    )
    print("✅ Superuser created successfully!")
    print(f"   Email: admin@localhost.com")
    print(f"   Password: admin@123")

print("\n📝 Django Admin Credentials:")
print("=" * 50)
print("URL: http://localhost:8000/admin/")
print("Email: admin@localhost.com")
print("Password: admin@123")
print("=" * 50)

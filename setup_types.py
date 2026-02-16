import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import SuperAdminType

# Create SuperAdmin types
types_data = [
    ('Admin', 'Full administrative access with all permissions', 3),
    ('Manager', 'Manager with content moderation and user management permissions', 2),
    ('Editor', 'Editor with limited permissions for content management', 1)
]

for name, description, permissions_level in types_data:
    obj, created = SuperAdminType.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'permissions_level': permissions_level
        }
    )
    status = '✓ Created' if created else '✓ Already exists'
    print(f"{status}: {name}")

print("\nSuperAdmin types setup complete!")

"""
Script to create SuperAdmin types in the database
Run with: python manage.py shell < create_superadmin_types.py
"""

from blog.models import SuperAdminType

# Create SuperAdmin types if they don't exist
admin_types = [
    {
        'name': 'Admin',
        'description': 'Full administrative access with all permissions',
        'permissions_level': 3
    },
    {
        'name': 'Manager',
        'description': 'Manager with content moderation and user management permissions',
        'permissions_level': 2
    },
    {
        'name': 'Editor',
        'description': 'Editor with limited permissions for content management',
        'permissions_level': 1
    }
]

for admin_type in admin_types:
    obj, created = SuperAdminType.objects.get_or_create(
        name=admin_type['name'],
        defaults={
            'description': admin_type['description'],
            'permissions_level': admin_type['permissions_level']
        }
    )
    if created:
        print(f"✓ Created SuperAdmin Type: {obj.name}")
    else:
        print(f"✓ SuperAdmin Type already exists: {obj.name}")

print("\nSuperAdmin types setup complete!")

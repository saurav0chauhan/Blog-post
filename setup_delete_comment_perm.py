#!/usr/bin/env python
"""
Script to add delete_comment permission to roles
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import Permission, Role, RolePermission

print("\n=== Adding Delete Comment Permission ===\n")

# Create the can_delete_comment permission
perm, created = Permission.objects.get_or_create(
    name='can_delete_comment'
)

if created:
    print("✓ Created 'can_delete_comment' permission")
else:
    print("✓ 'can_delete_comment' permission already exists")

# Assign permission to Writer role (writers should be able to delete their own comments)
try:
    writer_role = Role.objects.get(name='writer')
    rp, created = RolePermission.objects.get_or_create(
        role=writer_role,
        permission=perm
    )
    if created:
        print(f"✓ Assigned 'can_delete_comment' to Writer role")
    else:
        print(f"✓ Writer role already has 'can_delete_comment'")
except Role.DoesNotExist:
    print("⚠️  Writer role not found")

# You can also assign to Reader role if needed
try:
    reader_role = Role.objects.get(name='reader')
    rp, created = RolePermission.objects.get_or_create(
        role=reader_role,
        permission=perm
    )
    if created:
        print(f"✓ Assigned 'can_delete_comment' to Reader role")
    else:
        print(f"✓ Reader role already has 'can_delete_comment'")
except Role.DoesNotExist:
    print("⚠️  Reader role not found")

print("\n✅ Permission setup complete!")
print("\nNote: Users can delete their own comments or comments on their own blogs.")
print("Users with 'can_delete_comment' permission can delete any comment.\n")

# Show current permissions
print("=== Current Permissions ===")
all_perms = Permission.objects.all()
for perm in all_perms:
    print(f"  • {perm.name}")

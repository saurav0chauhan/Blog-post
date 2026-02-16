#!/usr/bin/env python
"""
Script to activate superadmin account
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import SuperAdmin

print("\n=== SuperAdmin Account Activation ===\n")

# Get all inactive superadmins
inactive_superadmins = SuperAdmin.objects.filter(is_active=False)

if inactive_superadmins.count() == 0:
    print("✅ No inactive superadmins found. All accounts are already active!")
    
    # Show active superadmins
    active = SuperAdmin.objects.filter(is_active=True)
    if active.count() > 0:
        print("\nActive SuperAdmins:")
        for admin in active:
            print(f"  ✓ {admin.email} ({admin.name}) - Type: {admin.admin_type.name if admin.admin_type else 'N/A'}")
else:
    print(f"Found {inactive_superadmins.count()} inactive superadmin(s):\n")
    
    for i, admin in enumerate(inactive_superadmins, 1):
        print(f"{i}. Email: {admin.email}")
        print(f"   Name: {admin.name}")
        print(f"   Company: {admin.company or 'N/A'}")
        print(f"   Type: {admin.admin_type.name if admin.admin_type else 'N/A'}")
        print(f"   Created: {admin.created_at}\n")
    
    # Activate all inactive superadmins
    inactive_superadmins.update(is_active=True)
    
    print("=" * 50)
    print("✅ All superadmin accounts activated successfully!\n")
    
    # Show updated status
    print("Updated SuperAdmins:")
    for admin in SuperAdmin.objects.all():
        status = "🟢 ACTIVE" if admin.is_active else "🔴 INACTIVE"
        print(f"  {status} - {admin.email} ({admin.name}) - Type: {admin.admin_type.name if admin.admin_type else 'N/A'}")

print("\n" + "="*50)
print("SuperAdmin Login URL: http://localhost:8000/superadmin/login/")
print("="*50 + "\n")

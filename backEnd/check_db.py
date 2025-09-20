#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backEnd.settings')
django.setup()

from django.db import connection

print("=== Database Connection Info ===")
print(f"Database Engine: {connection.settings_dict['ENGINE']}")
print(f"Database Name: {connection.settings_dict['NAME']}")
print(f"Database Host: {connection.settings_dict.get('HOST', 'N/A')}")
print(f"Database Port: {connection.settings_dict.get('PORT', 'N/A')}")
print(f"Database User: {connection.settings_dict.get('USER', 'N/A')}")

# Test connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"Database Version: {result[0]}")
        print("✓ Successfully connected to PostgreSQL")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    print("This means Django is likely using SQLite instead of PostgreSQL")
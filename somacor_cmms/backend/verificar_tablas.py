import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmms_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'checklist%'")
tablas = [row[0] for row in cursor.fetchall()]

print("Tablas de checklist en la base de datos:")
for tabla in tablas:
    print(f"  - {tabla}")

if not tablas:
    print("  ❌ No hay tablas de checklist")

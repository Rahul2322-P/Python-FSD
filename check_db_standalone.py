import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainable_living_platform.settings')
django.setup()
from django.db import connection
tables = connection.introspection.table_names()
print(f"Total Tables: {len(tables)}")
for table in tables:
    print(f"- {table}")

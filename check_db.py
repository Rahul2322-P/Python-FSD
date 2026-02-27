from django.db import connection
tables = connection.introspection.table_names()
print(f"Total Tables: {len(tables)}")
for table in tables:
    print(f"- {table}")

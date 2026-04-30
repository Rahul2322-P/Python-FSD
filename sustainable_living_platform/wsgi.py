import os
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainable_living_platform.settings')

django.setup()

# Automatically apply migrations in the deployed environment.
# This ensures the Vercel /tmp SQLite database is initialized before requests.
call_command('migrate', interactive=False, verbosity=0)

application = get_wsgi_application()

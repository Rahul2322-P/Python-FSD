import os
from django.core.management import call_command
from django.core.asgi import get_asgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainable_living_platform.settings')

django.setup()

# Automatically apply migrations in the deployed environment.
call_command('migrate', interactive=False, verbosity=0)

application = get_asgi_application()


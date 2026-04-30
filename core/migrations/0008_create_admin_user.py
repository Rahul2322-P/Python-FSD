from django.db import migrations


def create_admin_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    username = 'RAHUL'
    email = '2400032050@kluniversity.in'
    password = 'HONEY@2322'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_userprofile_is_email_verified_emailverification'),
    ]

    operations = [
        migrations.RunPython(create_admin_user),
    ]

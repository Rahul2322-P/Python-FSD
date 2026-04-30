from django.db import migrations


def create_additional_content(apps, schema_editor):
    LearningModule = apps.get_model('core', 'LearningModule')
    Challenge = apps.get_model('core', 'Challenge')

    additional_modules = [
        {
            'title': 'Waste Reduction Strategies',
            'description': 'Learn practical steps to reduce waste in your daily life and improve sustainability habits.',
            'content': '<p>Discover ways to avoid single-use plastics, reuse household items, and compost organic waste for a cleaner environment.</p>',
            'difficulty_level': 'beginner',
            'estimated_time': 15,
            'is_active': True,
        },
        {
            'title': 'Water Conservation Habits',
            'description': 'Build effective water-saving routines to protect one of our planet\'s most precious resources.',
            'content': '<p>Explore techniques for reducing water consumption, fixing leaks, and choosing water-friendly appliances.</p>',
            'difficulty_level': 'intermediate',
            'estimated_time': 18,
            'is_active': True,
        },
        {
            'title': 'Community Impact & Social Responsibility',
            'description': 'Understand how sustainable choices affect your community and how to lead change locally.',
            'content': '<p>Learn how to organize community cleanups, support local green businesses, and inspire others with sustainable actions.</p>',
            'difficulty_level': 'advanced',
            'estimated_time': 20,
            'is_active': True,
        },
    ]

    for module_data in additional_modules:
        LearningModule.objects.get_or_create(title=module_data['title'], defaults=module_data)

    additional_challenges = [
        {
            'title': 'Sustainable Shopping Challenge',
            'description': 'Buy only eco-friendly products for one week and compare your environmental savings.',
            'points': 20,
            'difficulty': 'medium',
            'repeatable': True,
            'is_active': True,
        },
        {
            'title': 'Smart Home Energy Audit',
            'description': 'Review your home energy use and switch off or replace inefficient devices.',
            'points': 25,
            'difficulty': 'hard',
            'repeatable': False,
            'is_active': True,
        },
        {
            'title': 'Urban Garden Starter',
            'description': 'Begin a small garden using sustainable materials, even in a limited space.',
            'points': 15,
            'difficulty': 'easy',
            'repeatable': True,
            'is_active': True,
        },
        {
            'title': 'Public Transport Week',
            'description': 'Use public or shared transport for a full week and track your reduced emissions.',
            'points': 30,
            'difficulty': 'hard',
            'repeatable': False,
            'is_active': True,
        },
    ]

    for challenge_data in additional_challenges:
        Challenge.objects.get_or_create(title=challenge_data['title'], defaults=challenge_data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_initial_learning_content'),
    ]

    operations = [
        migrations.RunPython(create_additional_content),
    ]

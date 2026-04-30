from django.db import migrations


def create_initial_learning_content(apps, schema_editor):
    LearningModule = apps.get_model('core', 'LearningModule')
    Challenge = apps.get_model('core', 'Challenge')

    modules = [
        {
            'title': 'Sustainable Home Habits',
            'description': 'Learn simple daily habits to reduce waste and save energy at home.',
            'content': '<p>Understand how small changes like switching to LED lighting, reducing water usage, and recycling can make a big environmental impact.</p>',
            'difficulty_level': 'beginner',
            'estimated_time': 12,
            'is_active': True,
        },
        {
            'title': 'Plastic-Free Living',
            'description': 'Understand plastic alternatives and how to reduce single-use plastics in daily life.',
            'content': '<p>Explore reusable options, plastic-free shopping tips, and how to choose sustainable materials.</p>',
            'difficulty_level': 'intermediate',
            'estimated_time': 18,
            'is_active': True,
        },
        {
            'title': 'Energy Efficient Transportation',
            'description': 'Discover eco-friendly travel choices and how to reduce your carbon footprint on the move.',
            'content': '<p>Compare walking, cycling, public transport, and vehicle sharing to find the most sustainable transportation choices.</p>',
            'difficulty_level': 'advanced',
            'estimated_time': 20,
            'is_active': True,
        },
    ]

    for module_data in modules:
        LearningModule.objects.get_or_create(title=module_data['title'], defaults=module_data)

    challenges = [
        {
            'title': 'Zero Waste Challenge',
            'description': 'Spend one day producing no plastic or paper waste and record your progress.',
            'points': 20,
            'difficulty': 'medium',
            'repeatable': False,
            'is_active': True,
        },
        {
            'title': 'Plant-Based Meal',
            'description': 'Prepare a fully plant-based meal and share your recipe to inspire others.',
            'points': 15,
            'difficulty': 'easy',
            'repeatable': True,
            'is_active': True,
        },
        {
            'title': 'Energy Audit',
            'description': 'Review your home energy use and switch off devices when not in use.',
            'points': 25,
            'difficulty': 'hard',
            'repeatable': False,
            'is_active': True,
        },
    ]

    for challenge_data in challenges:
        Challenge.objects.get_or_create(title=challenge_data['title'], defaults=challenge_data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_create_admin_user'),
    ]

    operations = [
        migrations.RunPython(create_initial_learning_content),
    ]

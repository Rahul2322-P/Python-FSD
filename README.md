# PS23 – Sustainable Living Education Platform

## Problem Description
Environmental sustainability requires awareness and behavioral change. This platform educates users about eco-friendly practices and sustainable living. Interactive challenges motivate users to adopt green habits. Progress tracking encourages consistency. Django manages learning content and user engagement.

## Core Features
- **Learning modules**: Read educational content, tips, and tutorials for sustainable action.
- **Challenges**: Commit to green habits like going zero-waste or vegetarian for a week to earn points.
- **Progress tracking**: Monitor total completed modules/challenges and keep score.

## Roles & Description
**Admin**
- Description: Updates sustainability content, creates new modules, and modifies point values.

**User**
- Description: Learns and applies practices by creating a standard profile, engaging with content, and completing challenges.

*Successfully built utilizing Django, Python, PostgreSQL, HTML5, CSS3, and Bootstrap 5!*

## Database Setup

For PostgreSQL 13, set the database environment variables before running the app:

- `USE_POSTGRES=True`
- `DB_NAME=<your_database_name>`
- `DB_USER=<your_database_user>`
- `DB_PASSWORD=<your_database_password>`
- `DB_HOST=<your_database_host>`
- `DB_PORT=<your_database_port>`

Example local settings for PostgreSQL 13:

```powershell
$env:USE_POSTGRES = 'True'
$env:DB_NAME = 'ecolearn'
$env:DB_USER = 'postgres'
$env:DB_PASSWORD = '1234'
$env:DB_HOST = 'localhost'
$env:DB_PORT = '5432'
```

Then run:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
# Edit .env if needed, then:
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py runserver
```

## Admin credentials created automatically
- Username: `RAHUL`
- Email: `2400032050@kluniversity.in`
- Password: `HONEY@2322`
- Admin secret code: `HONEY`


import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from apps.user.models import User

# Replace with your desired username, email, password
username = "admin"
email = "admin@example.com"
first_name = "Admin"
password = "adminpassword"

if not User.objects.filter(username=username,email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")

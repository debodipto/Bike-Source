import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update a superuser from environment variables."

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.environ.get("ADMIN_USERNAME", settings.DEFAULT_ADMIN_USERNAME))
        parser.add_argument("--email", default=os.environ.get("ADMIN_EMAIL", settings.DEFAULT_ADMIN_EMAIL))
        parser.add_argument("--password", default=os.environ.get("ADMIN_PASSWORD", settings.DEFAULT_ADMIN_PASSWORD))

    def handle(self, *args, **options):
        username = (options.get("username") or "").strip()
        email = (options.get("email") or "").strip()
        password = options.get("password") or ""

        if not username:
            raise CommandError("Missing admin username. Set ADMIN_USERNAME or pass --username.")
        if not email:
            raise CommandError("Missing admin email. Set ADMIN_EMAIL or pass --email.")
        if not password:
            raise CommandError("Missing admin password. Set ADMIN_PASSWORD or pass --password.")

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{username}'"))

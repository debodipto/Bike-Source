from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class EnsureAdminCommandTests(TestCase):
    def test_ensure_admin_creates_superuser(self):
        call_command(
            "ensure_admin",
            username="renderadmin",
            email="render@example.com",
            password="StrongPass123",
        )

        user = get_user_model().objects.get(username="renderadmin")
        self.assertEqual(user.email, "render@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("StrongPass123"))

    def test_ensure_admin_updates_existing_superuser(self):
        user = get_user_model().objects.create_superuser(
            username="renderadmin",
            email="old@example.com",
            password="OldPass123",
        )

        call_command(
            "ensure_admin",
            username="renderadmin",
            email="new@example.com",
            password="NewPass123",
        )

        user.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password("NewPass123"))

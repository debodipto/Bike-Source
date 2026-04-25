from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def ensure_default_admin(sender, **kwargs):
    username = (getattr(settings, "DEFAULT_ADMIN_USERNAME", "") or "").strip()
    email = (getattr(settings, "DEFAULT_ADMIN_EMAIL", "") or "").strip()
    password = getattr(settings, "DEFAULT_ADMIN_PASSWORD", "") or ""

    if not username or not email or not password:
        return

    user_model = get_user_model()
    user, _ = user_model.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    updated_fields = []
    if user.email != email:
        user.email = email
        updated_fields.append("email")
    if not user.is_staff:
        user.is_staff = True
        updated_fields.append("is_staff")
    if not user.is_superuser:
        user.is_superuser = True
        updated_fields.append("is_superuser")
    if not user.check_password(password):
        user.set_password(password)
        updated_fields.append("password")

    if updated_fields:
        user.save()


from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        elif self.role == self.Role.ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

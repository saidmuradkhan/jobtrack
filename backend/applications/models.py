from django.conf import settings
from django.db import models
from django.utils import timezone


class Application(models.Model):
    class Status(models.TextChoices):
        WISHLIST = "wishlist", "Wishlist"
        APPLIED = "applied", "Applied"
        INTERVIEW = "interview", "Interview"
        OFFER = "offer", "Offer"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    applied_on = models.DateField(default=timezone.localdate)
    salary = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="AZN")
    url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_on", "-created_at"]

    def __str__(self):
        return f"{self.position} at {self.company}"

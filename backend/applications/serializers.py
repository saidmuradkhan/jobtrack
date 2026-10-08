from rest_framework import serializers

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "company",
            "position",
            "status",
            "applied_on",
            "salary",
            "currency",
            "url",
            "notes",
            "vacancy_uid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_currency(self, value):
        value = value.strip().upper()
        if len(value) != 3 or not value.isalpha():
            raise serializers.ValidationError("Use a 3-letter currency code, e.g. AZN or USD.")
        return value

    def validate_vacancy_uid(self, value):
        value = value.strip()
        if not value:
            return value
        user = self.context["request"].user
        taken = Application.objects.filter(user=user, vacancy_uid=value)
        if self.instance:
            taken = taken.exclude(pk=self.instance.pk)
        if taken.exists():
            raise serializers.ValidationError("You already saved this vacancy.")
        return value

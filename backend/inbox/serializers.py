from rest_framework import serializers

from applications.models import Application

from .models import InboundEmail


class LinkedApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "company", "position", "status"]


class InboundEmailSerializer(serializers.ModelSerializer):
    application = LinkedApplicationSerializer(read_only=True)

    class Meta:
        model = InboundEmail
        fields = [
            "id",
            "sender",
            "subject",
            "snippet",
            "status",
            "company",
            "position",
            "outcome",
            "previous_status",
            "application",
            "received_at",
        ]

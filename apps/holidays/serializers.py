from rest_framework import serializers
from apps.holidays.models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    """
    Full serializer for Holiday model with all details
    """

    branch_name = serializers.CharField(
        source="branch.name", read_only=True, allow_null=True
    )
    company_name = serializers.CharField(source="branch.company.name", read_only=True)

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "description",
            "branch",
            "branch_name",
            "company_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HolidayListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing holidays
    """

    branch_name = serializers.CharField(
        source="branch.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Holiday
        fields = [
            "id",
            "name",
            "date",
            "branch",
            "branch_name",
        ]
        read_only_fields = ["id"]


class HolidayCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating holidays
    """

    class Meta:
        model = Holiday
        fields = [
            "name",
            "date",
            "description",
            "branch",
        ]

    def validate_date(self, value):
        """
        Validate that the holiday date is not in the past
        """
        from datetime import date

        if value < date.today():
            raise serializers.ValidationError(
                "Holiday date cannot be in the past (for new holidays)"
            )
        return value

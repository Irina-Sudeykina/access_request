from rest_framework import serializers

from mis.models import InformationSystem, InformationSystemRole, AccessRequest
# from habits.validators import (validate_frequency, validate_linked_habit_and_reward, validate_linked_habit_is_pleasant,
                               # validate_pleasant_habit_no_rewards_or_links, validate_time_to_complete)


class InformationSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationSystem
        fields = "__all__"


class InformationSystemRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = InformationSystemRole
        fields = "__all__"


class AccessRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRequest
        fields = "__all__"

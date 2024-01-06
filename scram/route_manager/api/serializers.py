import logging

from netfields import rest_framework
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from simple_history.utils import update_change_reason

from ..models import ActionType, Client, Entry, IgnoreEntry, Route

logger = logging.getLogger(__name__)


class ActionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionType
        fields = ["pk", "name", "available"]


class RouteSerializer(serializers.ModelSerializer):
    route = rest_framework.CidrAddressField()

    class Meta:
        model = Route
        fields = [
            "route",
        ]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["hostname", "uuid"]


class EntrySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:v1:entry-detail", lookup_url_kwarg="pk", lookup_field="route"
    )
    route = rest_framework.CidrAddressField()
    actiontype = serializers.CharField(default="block")
    if CurrentUserDefault():
        # This is set if we are calling this serializer from WUI
        who = CurrentUserDefault()
    else:
        who = serializers.CharField()
    comment = serializers.CharField()

    class Meta:
        model = Entry
        fields = ["route", "actiontype", "url", "comment", "who"]

    def get_comment(self, obj):
        return obj.get_change_reason()

    def create(self, validated_data):
        valid_route = validated_data.pop("route")
        actiontype = validated_data.pop("actiontype")
        comment = validated_data.pop("comment")

        route_instance, created = Route.objects.get_or_create(route=valid_route)
        actiontype_instance = ActionType.objects.get(name=actiontype)
        entry_instance, created = Entry.objects.get_or_create(route=route_instance, actiontype=actiontype_instance)

        logger.debug(f"{comment}")
        update_change_reason(entry_instance, comment)

        return entry_instance


class IgnoreEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = IgnoreEntry
        fields = ["route", "comment"]

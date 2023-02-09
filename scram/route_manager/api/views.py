import ipaddress
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import ActionType, Entry, IgnoreEntry
from .exceptions import IgnoredRoute, PrefixTooLarge
from .serializers import ActionTypeSerializer, EntrySerializer, IgnoreEntrySerializer

channel_layer = get_channel_layer()


class ActionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActionType.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ActionTypeSerializer
    lookup_field = "name"


class IgnoreEntryViewSet(viewsets.ModelViewSet):
    queryset = IgnoreEntry.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = IgnoreEntrySerializer
    lookup_field = "route"


class EntryViewSet(viewsets.ModelViewSet):
    queryset = Entry.objects.filter(is_active=True)
    permission_classes = (IsAuthenticated,)
    serializer_class = EntrySerializer
    lookup_value_regex = ".*"
    http_method_names = ["get", "post", "head", "delete"]

    def perform_create(self, serializer):
        logging.debug(f"{serializer.validated_data}")
        actiontype = serializer.validated_data["actiontype"]
        route = serializer.validated_data["route"]
        # comment = serializer.validated_data["comment"]
        # tmp_exp = self.request.POST.get("expiration", "")
        #
        # try:
        #     expiration = parse_datetime(tmp_exp)  # noqa: F841
        # except ValueError:
        #     logging.info(f"Could not parse expiration DateTime string {tmp_exp!r}.")

        # min_prefix = getattr(settings, f"V{route.version}_MINPREFIX", 0)
        # if route.prefixlen < min_prefix:
        #     raise PrefixTooLarge()

        # Don't process if we have the entry in the ignorelist
        overlapping_ignore = IgnoreEntry.objects.filter(route__net_overlaps=route)
        if overlapping_ignore.count():
            ignore_entries = []
            for ignore_entry in overlapping_ignore.values():
                ignore_entries.append(str(ignore_entry["route"]))
            logging.info(
                f"Cannot proceed adding {route}. The ignore list contains {ignore_entries}"
            )
            raise IgnoredRoute
        else:
            # Must match a channel name defined in asgi.py
            async_to_sync(channel_layer.group_send)(
                f"translator_{actiontype}",
                {"type": "translator_add", "message": {"route": str(route)}},
            )

    #
    #         # entry = Entry.objects.get(route__route=route, actiontype__name=actiontype)
    #         # if expiration:
    #         #     entry.expiration = expiration
    #         # entry.is_active = True
    #         # entry.who = self.request.user.username
    #         # entry.comment = comment
    #         # logging.info(f"{entry}")
    #         # entry.save()

    @staticmethod
    def find_entries(arg, active_filter=None):
        if not arg:
            return Entry.objects.none()

        # Is our argument an integer?
        try:
            pk = int(arg)
            query = Q(pk=pk)
        except ValueError:
            # Maybe a CIDR? We want the ValueError at this point, if not.
            cidr = ipaddress.ip_network(arg, strict=False)

            min_prefix = getattr(settings, f"V{cidr.version}_MINPREFIX", 0)
            if cidr.prefixlen < min_prefix:
                raise PrefixTooLarge()

            query = Q(route__route__net_overlaps=cidr)

        if active_filter is not None:
            query &= Q(is_active=active_filter)

        return Entry.objects.filter(query)

    def retrieve(self, request, pk=None, **kwargs):
        entries = self.find_entries(pk, active_filter=True)
        # TODO: What happens if we get multiple? Is that ok? I think yes, and return them all?
        if entries.count() != 1:
            raise Http404
        serializer = EntrySerializer(entries, many=True, context={"request": request})
        return Response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        for entry in self.find_entries(pk, active_filter=True):
            entry.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

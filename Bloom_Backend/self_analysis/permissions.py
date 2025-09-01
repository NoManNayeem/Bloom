# self_analysis/permissions.py
from __future__ import annotations

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Read-only for everyone authenticated; writes only for staff/admins.
    SAFE_METHODS = GET, HEAD, OPTIONS.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level check: allow if the requesting user owns the object
    (expects the object to have a `user` FK), or the requester is staff.
    Useful for Answer objects if you ever expose detail routes.
    """
    def has_object_permission(self, request, view, obj):
        # Read allowed for the owner (and staff), write allowed for owner (and staff)
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        owner_id = getattr(obj, "user_id", None)
        return owner_id == request.user.id

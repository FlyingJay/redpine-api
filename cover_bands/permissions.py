from rest_framework import permissions

class CoverLeadPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == 'POST'

    def has_permission(self, request, view):
        return request.method == 'POST'

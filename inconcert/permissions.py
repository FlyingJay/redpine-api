from rest_framework import permissions

class PreRegistrationPermission(permissions.BasePermission):
    """ pre-registrations can only be created """
    def has_permission(self, request, view):
        return request.method == 'POST'

    def has_object_permission(self, request, view, obj):
        return request.method == 'POST'

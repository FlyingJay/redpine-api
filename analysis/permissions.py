from rest_framework import permissions

class AnalysisPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == 'GET'

    def has_permission(self, request, view):
        return request.method == 'GET'

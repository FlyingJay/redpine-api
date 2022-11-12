from rest_framework.exceptions import APIException, ValidationError


class BadRequest(APIException):
    status_code = 400
    default_detail = 'We were unable to process your request'
    default_code = 'bad_request'

class PermissionDenied(APIException):
    status_code = 403
    default_detail = 'You\'re not allowed sry.'
    default_code = 'permission_denied'

class MembershipError(APIException):
    status_code = 420
    default_detail = 'Membership is required.'
    default_code = 'membership_error'
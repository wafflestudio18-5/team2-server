from rest_framework.permissions import BasePermission


class UserAccessPermission(BasePermission):
    message = "Cannot query 'public' for user other than 'me'"

    def has_permission(self, request, view):
        return not ('public' in request.query_params and view.kwargs['pk'] != 'me') \
               and not (view.kwargs['pk'] == 'me' and request.user.is_anonymous)

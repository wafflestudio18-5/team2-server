from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StoryPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(self.get_paginated_data(data))

    def get_paginated_data(self, data):
        return {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'stories': data
        }

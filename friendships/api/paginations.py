from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # default page size, when page not specified in url param
    page_size = 20
    # default is None, user cannot specify the page size
    # but if set, then user can specify page size by typing 'size=10' to set the page size
    # app or web end need different page size even though using the same API
    page_size_query_param = 'size'
    # the allowed maximum page size
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data,
        })


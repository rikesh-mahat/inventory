from rest_framework import pagination
# from rest_framework.response import Response

class MyPagination(pagination.LimitOffsetPagination):
    default_limit = 2
    limit_query_param = "l"
    offset_query_param = "o"
    max_limit = 4
    
# class CustomPagination(pagination.PageNumberPagination):
#     def get_paginated_response(self, data):
#         return Response({
#             "links": {
#                 "next": self.get_next_link,
#                 "previous": self.get_previous_link
#             },
#             "count": self.page.paginator.count,
#             "results": data
#         })
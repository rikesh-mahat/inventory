from rest_framework import pagination
# from rest_framework.response import Response

class MyPagination(pagination.PageNumberPagination):
    # default_limit = 5
    # max_limit = 10
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100
    last_page_strings = ('verylast',)
    
class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 5
    max_limit = 100
    limit_query_param = 'limit'
    offset_query_param = 'offset'


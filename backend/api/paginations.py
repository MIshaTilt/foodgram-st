from rest_framework.pagination import PageNumberPagination

from .constants import DEFAULT_PAGE_SIZE, PAGE_SIZE_QUERY_PARAM


class LimitPageNumberPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = PAGE_SIZE_QUERY_PARAM

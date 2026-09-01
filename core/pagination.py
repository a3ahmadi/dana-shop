from rest_framework.pagination import CursorPagination
from rest_framework.pagination import LimitOffsetPagination

class CursorPaginations(CursorPagination):
    page_size = 10
    ordering = ("-created_at", "-id")


class LimitOffsetPaginations(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100

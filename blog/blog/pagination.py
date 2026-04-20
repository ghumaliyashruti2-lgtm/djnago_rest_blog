from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination,CursorPagination
from rest_framework.response import Response

'''class NumPagination(PageNumberPagination):

    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 10
    
    def get_paginated_response(self, data):
        return Response({
            "message": "Success",
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "data": data
        })
'''        
class NumPagination(LimitOffsetPagination):

    # url .. ?limit=3&offset=2(here limit is number of record and offset start with that record number)
    
    default_limit = 1
    # its show 5 record per page (its used when user not set limit and offset in your url )
    limit_query_param = 'mylimit'
    # instead of a name limit to mylimit (url .. ?mylimit=3&offset=2)
    offset_query_param = 'myoffset'
    # instead of name offset to myoffset (url .. ?mylimit=3&myoffset=2)
    max_limit = 3
    # show max 3 record per page . 

'''
class NumPagination(CursorPagination):
    page_size = 1 # number of record show per page 
    ordering = "is_private" # cursor pagination work based on data like id , name , date , etc ..
    # here we want data base on user . 
    cursor_query_param = "mycursor"
    # instead name cursor to my cursor 
'''
    
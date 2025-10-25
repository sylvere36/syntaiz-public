from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import urllib.parse as urlparse
from urllib.parse import parse_qs


def getPage(url):
    if url is None:
        return None
    parsed = urlparse.urlparse(url)
    if "page" not in parse_qs(parsed.query):
        return 1
    ret = parse_qs(parsed.query)['page']
    if isinstance(ret, list):
        return int(ret[0])
    elif isinstance(ret, str):
        return int(ret)
    elif isinstance(ret, int):
        return ret
    else:
        return ret


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'next_num': getPage(self.get_next_link()),
                'previous_num': getPage(self.get_previous_link())
            },
            'max_page_size': self.max_page_size,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'results': data
        })
    
    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'links': {
                    'type': 'object',
                    'properties': {
                        'next': {
                            'type': ['string', 'null'],
                            'format': 'uri',
                            'description': 'Link to the next page of results'
                        },
                        'previous': {
                            'type': ['string', 'null'],
                            'format': 'uri',
                            'description': 'Link to the previous page of results'
                        },
                        'next_num': {
                            'type': 'integer',
                            'description': 'Next num'
                        },
                        'previous_num': {
                            'type': 'integer',
                            'description': 'Previous num'
                        },
                    }
                },
                'max_page_size': {
                    'type': 'integer',
                    'description': 'Max page'
                },
                'count': {
                    'type': 'integer',
                    'description': 'Total number of items available'
                },
                'total_pages': {
                    'type': 'integer',
                    'description': 'Total pages'
                },
                'results': {
                    'type': 'array',
                    'items': schema,
                    'description': 'List of paginated items'
                }
            }
        }
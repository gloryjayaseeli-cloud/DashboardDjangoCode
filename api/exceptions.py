import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        custom_data = {'error': response.data}
        response.data = custom_data
        return response

    logger.error(
        f"Unhandled exception occurred: {exc}",
        exc_info=True 
    )

    return Response(
        {'error': 'A server error occurred. Please try again later.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
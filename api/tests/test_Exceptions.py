from unittest.mock import patch
from django.urls import path, reverse
from django.test import override_settings 
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated

def some_function_that_might_fail():
    pass

class UnhandledExceptionView(APIView):
    def get(self, request):
        some_function_that_might_fail()
        return Response("This should not be reached.")

class HandledExceptionView(APIView):
    def get(self, request):
        raise NotAuthenticated()

urlpatterns = [
    path('unhandled-error/', UnhandledExceptionView.as_view(), name='unhandled_error'),
    path('handled-error/', HandledExceptionView.as_view(), name='handled_error'),
]

@override_settings(ROOT_URLCONF='api.tests.test_Exceptions')
class CustomExceptionHandlerTest(APITestCase):

    @patch('api.tests.test_Exceptions.some_function_that_might_fail')
    @patch('api.exceptions.logger')
    def test_handler_catches_unhandled_exception(self, mock_logger, mock_failing_function):
        mock_failing_function.side_effect = ValueError("Simulated error")
        response = self.client.get(reverse('unhandled_error')) 
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data,   {'error': 'A server error occurred. Please try again later.'})
        self.assertTrue(mock_logger.error.called)

    def test_handler_wraps_standard_drf_exception(self):
        response = self.client.get(reverse('handled_error')) 
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        expected_detail = {'detail': 'Authentication credentials were not provided.'}
        self.assertEqual(response.data, {'error': expected_detail})
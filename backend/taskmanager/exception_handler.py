from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    if isinstance(response.data, dict):
        if "detail" in response.data:
            response.data = {"error": response.data["detail"]}
        else:
            response.data = {"error": response.data}

    return response
from coreapi import Object
from django.http import JsonResponse
from rest_framework.views import exception_handler
from http import HTTPStatus
from typing import Any
from rest_framework import exceptions, status
from rest_framework.views import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException

def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Custom API exception handler."""

    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        
        error_payload = {
            "error": {
                "status_code": 0,
                "details": [],
            }
        }
        error = error_payload["error"]
        status_code = response.status_code
       
        error["status_code"] = status_code
        print(response.data)
        if status_code == 400:
            error["details"] = {
                "message":"Validation error",
                "code":"validation_error"
            }
            
            
            
            new_error = {}
            for field_name, field_errors in response.data.items():
                if not type(field_errors) is list and field_name == 'detail':
                    error["details"] = {"message": field_errors, "code":field_errors.code}
                elif type(field_errors) is list:
                    new_error[field_name] = {"message": field_errors[0], "code":field_errors[0].code}
                    error["fields"] = new_error
                else:
                    print(type(field_errors))
                    for field_name2, field_errors2 in field_errors.items():
                        new_error[field_name+"."+field_name2] = {"message": field_errors2[0], "code":field_errors2[0].code}
                        error["fields"] = new_error
        else:  
            for field_name, field_errors in response.data.items():
                if not type(field_errors) is list and field_name == 'detail':
                    error["details"] = {"message": field_errors, "code":field_errors.code}
                    
        response.data = error_payload
    return response


class DetailDictMixin:
    def __init__(self, detail=None, code=None):
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """
        detail_dict = {"detail": self.default_detail, "code": self.default_code}

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict["detail"] = detail

        if code is not None:
            detail_dict["code"] = code

        super().__init__(detail_dict)
        
class AuthenticationFailed(DetailDictMixin, exceptions.AuthenticationFailed):
    pass

def internal_server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    error_payload = {
        "error": {
            "status_code": 500,
            "details": {
                "message":"Internal server error",
                "code":"internal_server_error"
            }
        }
    }
    return JsonResponse(error_payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def not_found(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    error_payload = {
        "error": {
            "status_code": 404,
            "details": {
                "message":"Not found",
                "code":"not_found"
            }
        }
    }
    return JsonResponse(error_payload, status=status.HTTP_404_NOT_FOUND)

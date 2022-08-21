
from drf_yasg import openapi

class SwaggerResponses():
  def get_validation_error_schema():
    return openapi.Schema(
      'Validation Error',
      type=openapi.TYPE_OBJECT,
      properties={
        'error': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Error body',
            properties={
              'status_code': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                default=400,
                description='Status code of request'
              ),
              'details': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='Error info',
                properties={
                  'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Error message'
                  ),
                  'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Error code'
                  ),
              }),
              'fields': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='Error messages for each field that triggered a validation error',
                properties={
                    'email': openapi.Schema(
                      type=openapi.TYPE_OBJECT,
                      description='Field with error',
                      properties={
                        'message': openapi.Schema(
                          type=openapi.TYPE_STRING,
                          description='Error message'
                        ),
                        'code': openapi.Schema(
                          type=openapi.TYPE_STRING,
                          description='Error code'
                        ),
                      }
                    ),
                    'info.is_research': openapi.Schema(
                      type=openapi.TYPE_OBJECT,
                      description='Object field with error',
                      properties={
                        'message': openapi.Schema(
                          type=openapi.TYPE_STRING,
                          description='Error message'
                        ),
                        'code': openapi.Schema(
                          type=openapi.TYPE_STRING,
                          description='Error code'
                        ),
                      }
                    ),
                }
              )
            }
          )
        }
    )
    
  def get_common_schema(title, default_status_code=400, default_code="string"):
    return openapi.Schema(
      title,
      type=openapi.TYPE_OBJECT,
      properties={
        'error': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='Error body',
            properties={
              'status_code': openapi.Schema(
                type=openapi.TYPE_NUMBER,
                default=default_status_code,
                description='Status code of request'
              ),
              'details': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description='Error info',
                properties={
                  'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Error message'
                  ),
                  'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    default=default_code,
                    description='Error code'
                  ),
              })
            }
        )
      }
    )
    
  def get_success_schema(title, string="string"):
    return openapi.Schema(
      title,
      type=openapi.TYPE_OBJECT,
      properties={
        'success':  openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description=string
                  ),
      }
    )

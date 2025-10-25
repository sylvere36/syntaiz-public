from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

def custom_exception_handler(exc, context):
    # Appel du gestionnaire d'exception par défaut pour obtenir la réponse standard
    response = exception_handler(exc, context)

    if response is not None:
        # Cas particulier pour ValidationError pour formater les messages d'erreur
        if isinstance(exc, ValidationError):
            custom_response_data = {
                'error': True,
                'status_code': response.status_code,
                'message': response.data  # Garder la structure originale des messages d'erreur
            }
        else:
            custom_response_data = {
                'error': True,
                'status_code': response.status_code,
                'message': response.data.get('detail', str(exc))
            }
        response.data = custom_response_data
    else:
        # Si la réponse est None, nous gérons nous-mêmes l'exception non gérée
        custom_response_data = {
            'error': True,
            'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            'message': 'An internal server error occurred.'
        }
        response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response

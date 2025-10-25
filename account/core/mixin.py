from rest_framework.response import Response

class CustomResponseMixin:
    def get_custom_response(self, data, pagination=None):
        if isinstance(data, list):
            # Utiliser le nom pluriel du modèle
            model_name = self.queryset.model._meta.verbose_name_plural
        else:
            # Utiliser le nom singulier du modèle
            model_name = self.queryset.model._meta.verbose_name

        response_data = {
            'current_user': self.request.user.username,
            model_name: data
        }

        if pagination:
            response_data['pagination'] = pagination

        return Response(response_data)

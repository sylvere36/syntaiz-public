"""
URL configuration for APP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(custom_settings={
            'TITLE': 'SYNTAIZ API',
            'DESCRIPTION': "API web de SYNTAIZ",
            'CONTACT': {
                'name': 'Cauliflow',
                'url': 'https://cauliflow.com',
                'email': 'contact@cauliflow.com'
            },
            'LICENSE': {
                'name': "License"
            },
            'VERSION': '0.0.1'
        },), name='schema'),
    path('', SpectacularSwaggerView.as_view(
             template_name="swagger-ui.html", url_name="schema"
        ), name='schema-swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
    path('api/v1/', include(('APP.api_urls', 'api'), namespace="baseApi")),
]

from django.urls import include, path
from rest_framework import routers
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from drf_hello.quickstart import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('openapi', get_schema_view(public=True),
         name='openapi-schema'),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html.j2',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='redoc'),
]

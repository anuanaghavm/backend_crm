from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="CRM API",
        default_version='v1',
        description="API documentation for crm project",
        terms_of_service="https://www.yourproject.com/terms/",
        contact=openapi.Contact(email="theerthakk467@gmail.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
)

urlpatterns = [
    path('swagger<str:format>', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-schema-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),

]
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import ObtainAuthToken

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/login/', ObtainAuthToken.as_view()),
    path('doc/', schema_view.with_ui('swagger',
                                     cache_timeout=0), name='schema-swagger-ui'),
    path('student/', include('students.urls'))


]

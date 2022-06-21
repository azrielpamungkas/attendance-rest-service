from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import ObtainAuthToken

schema_view = get_schema_view(
    openapi.Info(
        title="Attendance Rest Service",
        default_version='v1',
        license=openapi.License(name="GNU GPLv3"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/login/', ObtainAuthToken.as_view()),
    path('api/v1/doc/', schema_view.with_ui('swagger',
                                            cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/student/', include('students.urls'))

]

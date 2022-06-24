from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema
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


class ObtainToken(ObtainAuthToken):
    """
        Untuk mendapatkan token harus post 'username' dan 'password'
    """
    response_schema_dict = {
        "200": openapi.Response(schema={'a': 'aa'}, description="", examples={
            "application/json": {
                "200_key1": "200_value_1",
                            "200_key2": "200_value_2",
            }
        })
    }

    @swagger_auto_schema(responses=response_schema_dict, request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        }
    ))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/login/', ObtainToken.as_view()),
    path('api/v1/doc/', schema_view.with_ui('swagger',
                                            cache_timeout=0), name='schema-swagger-ui'),
    path('api/v1/student/', include('students.urls')),
    path('api/v1/', include('apps.attendances.urls')),

]

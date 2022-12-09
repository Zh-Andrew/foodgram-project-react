from django.urls import include, path
from .views import CustomUserViewSet
from rest_framework import routers


app_name = 'users'

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

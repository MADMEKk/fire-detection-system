from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cameras', views.CameraViewSet)
router.register(r'fire-alerts', views.FireAlertViewSet)
router.register(r'profile', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('verify-fire/', views.verify_fire, name='verify-fire'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]

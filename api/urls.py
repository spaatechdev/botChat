from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name='api'
urlpatterns = [
    path('test-cors/', views.test_cors_view, name='test_cors_view'),
    path('login/', jwt_views.TokenObtainPairView.as_view(), name ='login'),
    path('login/refresh/', jwt_views.TokenRefreshView.as_view(), name ='login_refresh'),

    path('login-user/', views.loginUser, name ='login_user'),
    path('get-user-details/', views.getUserDetails, name ='get_user_details'),
    path('logout-user/', views.logoutUser, name ='logout_user'),

    path('get-response/', csrf_exempt(views.getResponse), name ='getResponse'),
]
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()

router.register('users', views.UsersViewSet)
router.register('bookings', views.BookingsViewSet)
router.register('fields', views.FieldsViewSet)
router.register('field_images', views.FieldImagesViewSet)
router.register(r'reviews', views.ReviewViewSet, basename='reviews')

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.LoginDataView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('owner/dashboard/', views.OwnerDashboardAPIView.as_view(), name='owner-dashboard'),
    path('auth/request-otp/', views.request_otp, name='request_otp'),
    path('auth/reset-password-otp/', views.reset_password_with_otp, name='reset_password_otp'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/me/delete-account/', views.delete_account, name='delete-account'),
    path('', include(router.urls)),
]
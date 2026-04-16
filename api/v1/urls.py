from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()

router.register('users', views.UsersViewSet)
router.register('bookings', views.BookingsViewSet)
router.register('fields', views.FieldsViewSet)
router.register('field_images', views.FieldImagesViewSet)

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.LoginDataView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
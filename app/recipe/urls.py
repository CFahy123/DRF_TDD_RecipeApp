from django.urls import (path, include)
from recipe import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

app_name = 'recipe' # for the reverse lookup of urls

urlpatterns = [
    path('', include(router.urls)),
    # path('token/',views.CreateTokenView.as_view(), name='token'),
    # path('me/',views.ManageUserView.as_view(), name='me'),
]
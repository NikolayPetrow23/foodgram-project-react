from app import views
from django.urls import include, path
from rest_framework import routers

app_name = 'app'

router = routers.DefaultRouter()
router.register('tags', views.TagViewSet, basename="tags")
router.register('recipes', views.RecipeViewSet, basename="recipes")
router.register(
    'ingredients',
    views.IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls)),
]

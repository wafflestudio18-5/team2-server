from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import StoryViewSet

app_name = 'story'

router = SimpleRouter()
router.register('story', StoryViewSet, basename='story')

urlpatterns = [
    path('', include((router.urls))),
]

from django.urls import path 
from . import views
urlpatterns = [
 path('analyze-win-percentage/',views.analyze_win_percentage),
]

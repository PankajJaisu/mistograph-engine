from django.urls import path 
from . import views
urlpatterns = [
 path('win-percentage/',views.win_percentage),
 path('profitable-pair/',views.profitable_pair),
 path('profitable-day/',views.profitable_day),
 path('analyze-win-percentage/',views.analyze_win_percentage),

]

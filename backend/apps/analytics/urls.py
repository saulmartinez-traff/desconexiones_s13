"""
Analytics App URLs
"""

from django.urls import path
from . import views

urlpatterns = [
    path('summary-matrix/', views.summary_matrix, name='summary-matrix'),
    path('group/<int:group_id>/stats/', views.group_stats, name='group-stats'),
    path('top-disconnected/', views.top_disconnected_vehicles, name='top-disconnected'),
]

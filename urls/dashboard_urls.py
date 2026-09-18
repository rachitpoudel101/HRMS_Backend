from django.urls import path
from apps.dashboard.views import dashboard_activities, dashboard_summary

urlpatterns = [
    path("dashboard/activities/", dashboard_activities, name="dashboard-activities"),
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
]

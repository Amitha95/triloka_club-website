from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from . import views
from .views import login_view, logout_view, dashboard_view, gallery_page, gallery_all,register_user,upload_gallery_image,gallery_list,upload_event, event_list
from .views import user_list,user_fees,user_points,user_fee_details,user_home, update_donation_status,point_redemption_rules, redeem_points
# Check if user is admin or staff
def is_admin(user):
    return user.is_superuser or user.is_staff

# Secure Admin Dashboard View
@user_passes_test(is_admin, login_url="/admin/login/")
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")  # Ensure this file exists

urlpatterns = [
    # Secure Admin Pages (Move Above /admin/)
    path("dashboard/", admin_dashboard, name="custom-admin-dashboard"),

    # Main App URLs
    path("", views.home, name="home"),
    path("base/", views.base, name="base"),
    path("about/", views.about, name="about"),
    path("events/", views.events_view, name="events"),
    path("gallery/", views.gallery_years, name="gallery_years"),  # Show date ranges
    path('gallery/', gallery_page, name='gallery_page'),
    path('api/gallery/', gallery_all, name='gallery_all'),
    path("gallery/<int:year_start>-<int:year_end>/", views.gallery_view, name="gallery"),
    path("contact/", views.contact, name="contact"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("dashboard_view/", dashboard_view, name="dashboard_view"),
    path("admin_dashboard/", admin_dashboard, name="admin_dashboard"),
    path("register_user/", register_user, name="register_user"),
    path("upload/", upload_gallery_image, name="upload_gallery"), 
    path("gallery_list/", gallery_list, name="gallery_list"),  
    path("upload-event/", upload_event, name="upload_event"),  # Event upload page
    path("event_list/", event_list, name="event_list"),  # Event list page
    path('users/', user_list, name='user_list'),
    path("users/fees/<int:user_id>/", user_fees, name="user_fees"),
    path("users/points/<int:user_id>/", user_points, name="user_points"),
    path("my-fees/", user_fee_details, name="user_fee_details"),
    path("user_home/", user_home, name="user_home"),
    path("update-donation-status/", update_donation_status, name="update_donation_status"),
    path('points/redemption/', point_redemption_rules, name='point_redemption_rules'),
    path('points/redeem/', redeem_points, name='redeem_points'),
    
    # Django Admin
    path("admin/", admin.site.urls),
]

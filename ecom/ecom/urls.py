"""
URL configuration for ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from store import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('profile/',views.profile,name="profile"),
    path("", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("home/", views.home_view, name="home"),
    # path("sign/", views.sign, name="sign"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("otp/", views.otp_verify, name="otp"),
    path("reset-otp/", views.reset_otp_verify, name="reset_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),
    path("refreshCaptcha/", views.refresh_captcha, name="refresh_captcha"),
    path("logout/", views.logout_view, name="logout"),
    path("apply-job/<int:job_id>/", views.apply_job, name="apply_job"),
    path("application/", views.application_view, name="applications"),
    path("application/<int:application_id>/", views.application_view, name="application_detail"),
    path("search-jobs/", views.search_jobs, name="search_jobs"),
    path("advice/", views.advice_view, name="advice"),
    path("contact/", views.contact_send, name="contact"),
    path("about/", views.about_view, name="about"),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
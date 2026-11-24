from django.contrib import admin
from django.urls import include, path
from accounts import views as account_views
from tasks.views import activity_page, home_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_page, name="home"),
    path("activity/", activity_page, name="activity"),
    path("login/", account_views.login_page, name="login"),
    path("register/", account_views.register_page, name="register"),
    path("logout/", account_views.logout_page, name="logout"),
    path("dashboard/", account_views.admin_dashboard_page, name="admin_dashboard"),
    path("dashboard/users/", account_views.admin_users_page, name="admin_users"),
    path("dashboard/tasks/", account_views.admin_tasks_page, name="admin_tasks"),
    path("api/accounts/", include("accounts.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/admin/", include("accounts.admin_urls")),
]

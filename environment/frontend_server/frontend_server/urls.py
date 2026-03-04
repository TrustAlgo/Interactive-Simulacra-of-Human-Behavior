from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from translator import views as translator_views


urlpatterns = [
    # Landing
    path("", translator_views.landing, name="landing"),

    # Simulator
    path("simulator_home/", translator_views.home, name="home"),

    # Demo
    path(
        "demo/<str:sim_code>/<str:step>/<str:play_speed>/",
        translator_views.demo,
        name="demo",
    ),

    # Replay
    path(
        "replay/<str:sim_code>/<str:step>/",
        translator_views.replay,
        name="replay",
    ),

    path(
        "replay_persona_state/<str:sim_code>/<str:step>/<str:persona_name>/",
        translator_views.replay_persona_state,
        name="replay_persona_state",
    ),

    # Environment
    path("process_environment/", translator_views.process_environment, name="process_environment"),
    path("update_environment/", translator_views.update_environment, name="update_environment"),

    # Path tester
    path("path_tester/", translator_views.path_tester, name="path_tester"),
    path("path_tester_update/", translator_views.path_tester_update, name="path_tester_update"),

    # Admin
    path("admin/", admin.site.urls),
]

# Serve static/media in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

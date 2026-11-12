from django.urls import path

from . import views

urlpatterns = [
    path("programmes/", views.ProgrammeListView.as_view(), name="programme_list"),
    path("programmes/new/", views.ProgrammeCreateView.as_view(), name="programme_create"),
    path("programmes/<int:pk>/", views.ProgrammeDetailView.as_view(), name="programme_detail"),
    path("programmes/<int:pk>/edit/", views.ProgrammeUpdateView.as_view(), name="programme_update"),
    path("programmes/<int:programme_pk>/speakers/new/", views.SpeakerCreateView.as_view(), name="speaker_create"),
    path("programmes/<int:programme_pk>/volunteers/new/", views.VolunteerCreateView.as_view(), name="volunteer_create"),
    path("programmes/<int:programme_pk>/followups/new/", views.FollowUpCreateView.as_view(), name="followup_create"),
    path("followups/<int:pk>/toggle/", views.followup_toggle, name="followup_toggle"),
]

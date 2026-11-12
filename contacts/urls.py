from django.urls import path

from . import views

urlpatterns = [
    path("contacts/", views.ContactListView.as_view(), name="contact_list"),
    path("contacts/new/", views.ContactCreateView.as_view(), name="contact_create"),
    path("contacts/<int:pk>/", views.ContactDetailView.as_view(), name="contact_detail"),
    path("contacts/<int:pk>/edit/", views.ContactUpdateView.as_view(), name="contact_update"),
    path("contacts/<int:contact_pk>/engagements/new/", views.InteractionCreateView.as_view(), name="interaction_create"),
    path("organisations/new/", views.OrganisationCreateView.as_view(), name="organisation_create"),
]

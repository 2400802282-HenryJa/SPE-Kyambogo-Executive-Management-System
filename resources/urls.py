from django.urls import path

from . import views

urlpatterns = [
    path("resources/", views.ResourceListView.as_view(), name="resource_list"),
    path("resources/new/", views.ResourceCreateView.as_view(), name="resource_create"),
    path("resources/<int:pk>/", views.ResourceDetailView.as_view(), name="resource_detail"),
    path("resources/<int:pk>/edit/", views.ResourceUpdateView.as_view(), name="resource_update"),
    path("resources/<int:item_pk>/movements/new/", views.MovementCreateView.as_view(), name="movement_create"),
    path("mobilisation/", views.MobilisationListView.as_view(), name="mobilisation_list"),
    path("mobilisation/new/", views.MobilisationCreateView.as_view(), name="mobilisation_create"),
    path("mobilisation/<int:pk>/edit/", views.MobilisationUpdateView.as_view(), name="mobilisation_update"),
]

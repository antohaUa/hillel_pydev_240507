from django.urls import path
import parcel.views

urlpatterns = [
    path('', parcel.views.parcels_view),
    path('<parcel_id>/', parcel.views.parcel_view)
]
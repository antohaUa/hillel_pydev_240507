from django.http import HttpResponse


def parcels_view(request):
    return HttpResponse('Parcels Endpoint')


def parcel_view(request, parcel_id):
    return HttpResponse(f'Parcel Endpoint ID: {parcel_id}')

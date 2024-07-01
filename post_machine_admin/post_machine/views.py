from django.http import HttpResponse


def post_machines_view(request):
    return HttpResponse('PostMachines Endpoint')


def post_machine_view(request, pm_id):
    return HttpResponse(f'PostMachine Endpoint ID: {pm_id}')


def post_machine_locker_view(request, pm_id, locker_id):
    return HttpResponse(f'PostMachine ID: {pm_id} -> Locker ID: {locker_id}')

from django.urls import path
import post_machine.views

urlpatterns = [
    path('', post_machine.views.post_machines_view),
    path('<pm_id>/', post_machine.views.post_machine_view),
    path('<pm_id>/<locker_id>', post_machine.views.post_machine_locker_view)
]
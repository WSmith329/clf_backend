from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .views import measurement_recording, create_payment_request, payments_index, send_payment_request, \
    set_starting_invoice_number, mark_payment_as_completed, mark_payment_as_void, process_selected_payments

urlpatterns = [
    path('measurement-recording/', login_required(measurement_recording), name='measurement_recording'),
    path('payments/<payment_status>/', staff_member_required(payments_index), name='payments_index'),
    path('create-payment-request/', staff_member_required(create_payment_request), name='create_payment_request'),
    path('update-payment-request/<int:pk>/', staff_member_required(create_payment_request),
         name='update_payment_request'),
    path('send-payment-request/<int:pk>/', staff_member_required(send_payment_request), name='send_payment_request'),
    path('mark-payment-as-completed/<int:pk>/', staff_member_required(mark_payment_as_completed),
         name='mark_payment_as_completed'),
    path('mark-payment-as-void/<int:pk>/', staff_member_required(mark_payment_as_void),
         name='mark_payment_as_void'),
    path('process-selected-payments/', staff_member_required(process_selected_payments),
         name='process_selected_payments'),
    path('starting-invoice-code/', staff_member_required(set_starting_invoice_number),
         name='set_starting_invoice_number')
]

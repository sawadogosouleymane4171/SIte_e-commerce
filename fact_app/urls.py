from django.urls import path
from .views import HomeView, AddCustomerView, AddInvoiceView, InvoiceVisualizationView, get_invoice_pdf, StatisticsView, change_language

urlpatterns = [
   path('', HomeView.as_view(), name='home'),
   path('add-customer', AddCustomerView.as_view(), name='add-customer'),
   path('add-invoice', AddInvoiceView.as_view(), name='add-invoice'),
   path('view-invoice/<int:pk>', InvoiceVisualizationView.as_view(), name='view-invoice'),
   path('invoice-pdf/<int:pk>', get_invoice_pdf, name='invoice-pdf'),
   path('statistics/', StatisticsView.as_view(), name='statistics'),
   path('change-language/<str:language_code>/', change_language, name='change_language'),
   path('change-language/', change_language, name='change_language'),
]
from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse 
import datetime
import pdfkit
import calendar
from django.db.models import Sum
from django.utils.translation import activate, get_language
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template.loader import get_template

from django.db import transaction

from .utils import pagination, get_invoice

from .decorators import *
from django.utils.translation import gettext as _
from django.db.models.functions import ExtractMonth  # Import nécessaire pour ExtractMonth


class HomeView(LoginRequiredSuperuserMixim, View):
    """
    Main view
    """
    templates_name = 'index.html'
    invoices = Invoice.objects.select_related('customer', 'save_by').all().order_by('-invoice_date_time')
    context = {'invoices': invoices}

    def get(self, request, *args, **kwargs):
        # Pagination
        default_page = 1
        page = request.GET.get('page', default_page)
        items_per_page = 3
        paginator = Paginator(self.invoices, items_per_page)

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)

        self.context['invoices'] = items_page
        return render(request, self.templates_name, self.context)

    def post(self, request, *args, **kwargs):
        # Modification d'une facture
        if request.POST.get('id_modified'):
            paid = request.POST.get('modified')
            try:
                obj = Invoice.objects.get(id=request.POST.get('id_modified'))
                obj.paid = True if paid == 'True' else False
                obj.save()
                messages.success(request, _("Change made successfully."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")

        # Suppression d'une facture
        if request.POST.get('id_supprimer'):
            try:
                obj = Invoice.objects.get(pk=request.POST.get('id_supprimer'))
                obj.delete()
                messages.success(request,_( "Invoice deleted successfully."))
            except Invoice.DoesNotExist:
                messages.error(request, _("Invoice not found. It may have already been deleted."))
            except Exception as e:
                messages.error(request, f"Sorry, the following error has occurred: {e}.")

        # Pagination après modification ou suppression
        default_page = 1
        page = request.GET.get('page', default_page)
        items_per_page = 3
        paginator = Paginator(self.invoices, items_per_page)

        try:
            items_page = paginator.page(page)
        except PageNotAnInteger:
            items_page = paginator.page(default_page)
        except EmptyPage:
            items_page = paginator.page(paginator.num_pages)

        self.context['invoices'] = items_page
        return render(request, self.templates_name, self.context)


class AddCustomerView(LoginRequiredSuperuserMixim,View):
    """
    Add new customer
    """
    template_name = "add_customer.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),
            'save_by': request.user if isinstance(request.user, User) else None
        }
        try:
            if data['save_by'] is None:
                messages.error(request, _("Invalid user. Please log in again."))
                return render(request, self.template_name)

            created = Customer.objects.create(**data)
            if created:
                messages.success(request, _("Customer registered successfully."))
            else:
                messages.error(request, _("Sorry, please try again. The sent data is corrupt."))
        except Exception as e:
            messages.error(request, f"Sorry, the following error has occurred: {e}.")
        return render(request, self.template_name)


class AddInvoiceView(LoginRequiredSuperuserMixim,View):
    """
    Add a new invoice view
    """
    template_name = 'add_invoice.html'
    customers = Customer.objects.select_related('save_by').all()
    context = {'customers': customers}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = []
        try:
            customer = request.POST.get('customer')
            invoice_type = request.POST.get('invoice_type')
            articles = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            total_a = request.POST.getlist('total-a')
            total = request.POST.get('total')
            comment = request.POST.get('comment')

            if not isinstance(request.user, User):
                messages.error(request, _("Invalid user. Please log in again."))
                return render(request, self.template_name, self.context)

            invoice_object = {
                'customer_id': customer,
                'save_by': request.user,
                'total': total,
                'invoice_type': invoice_type,
                'comments': comment
            }
            invoice = Invoice.objects.create(**invoice_object)

            for index, article in enumerate(articles):
                data = Article(
                    invoice_id=invoice.id,
                    name=article,
                    quantity=qties[index],
                    unit_price=units[index],
                    total=total_a[index],
                )
                items.append(data)

            created = Article.objects.bulk_create(items)
            if created:
                messages.success(request, _("Data saved successfully."))
            else:
                messages.error(request, _("Sorry, please try again. The sent data is corrupt."))
        except Exception as e:
            messages.error(request, f"Sorry, the following error has occurred: {e}.")
        return render(request, self.template_name, self.context)
    

class InvoiceVisualizationView( LoginRequiredSuperuserMixim,View):
    """
    This view helps to visualize the invoice
    """
    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):
        try:
            # Passez kwargs['pk'] à la fonction get_invoice
            context = get_invoice(kwargs['pk'])
        except Exception as e:
            return HttpResponse(f"An error occurred: {e}", status=400)

        return render(request, self.template_name, context)
    


@superuser_required
def get_invoice_pdf(request, *args, **kwargs) :
    """generate pdf file from html file
    """

    pk = kwargs.get('pk')

    context = get_invoice(pk)

    context['date'] = datetime.datetime.today()

    # get html file

    template = get_template('invoice-pdf.html')

    # render html with context variables

    html = template.render(context)

     # wkhtmltopdf path
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # options of pdf format

    options = {
        'page-size' : 'Letter',
        'encoding' : 'UTF-8',
        "enable-local-file-access": ""
    }
    # génère le PDF en mémoire
    pdf = pdfkit.from_string(
        html,
        False,
        options=options,
        configuration=config
    )
    # retourne la réponse
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{pk}.pdf"'
    return response


from django.utils.translation import activate
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def change_language(request):
    """
    Change the language and redirect to the current page.
    """
    if request.method == "POST":
        language_code = request.POST.get('language')
        if language_code:
            activate(language_code)
            request.session['django_language'] = language_code
    # Redirige vers la page précédente ou vers la page d'accueil si aucune page précédente n'est disponible
    return redirect(request.META.get('HTTP_REFERER', '/'))


from collections import defaultdict

class StatisticsView(LoginRequiredSuperuserMixim, View):
    """
    View for displaying statistics.
    """
    template_name = "statistics.html"

    def get(self, request, *args, **kwargs):
        # Revenus par mois
        monthly_revenue = (
            Invoice.objects.filter(paid=True)
            .annotate(month=ExtractMonth('invoice_date_time'))
            .values('month')
            .annotate(total=Sum('total'))
            .order_by('month')
        )

        # Préparer les données pour les graphiques
        revenue_dict = defaultdict(int, {item['month']: item['total'] for item in monthly_revenue})
        revenue_labels = [calendar.month_name[i] for i in range(1, 13)]
        revenue_data = [revenue_dict[i] for i in range(1, 13)]

        # Achats des clients par mois
        customer_purchases = (
            Article.objects.select_related('invoice')
            .values('invoice__customer__name')
            .annotate(total=Sum('total'))
            .order_by('-total')
        )
        purchases_labels = [item['invoice__customer__name'] for item in customer_purchases]
        purchases_data = [item['total'] for item in customer_purchases]

        context = {
            'revenue_labels': revenue_labels,
            'revenue_data': revenue_data,
            'purchases_labels': purchases_labels,
            'purchases_data': purchases_data,
        }
        return render(request, self.template_name, context)
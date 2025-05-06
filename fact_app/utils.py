from django.core.paginator import (Paginator, EmptyPage, PageNotAnInteger)

from .models import *
from django.http import HttpResponse 
def pagination(request, invoices):
    # default_page 
        default_page = 1 

        page = request.GET.get('page', default_page)

        # paginate items

        items_per_page = 3

        paginator = Paginator(invoices, items_per_page)

        try:

            items_page = paginator.page(page)

        except PageNotAnInteger:

            items_page = paginator.page(default_page)

        except EmptyPage:

            items_page = paginator.page(paginator.num_pages) 

        return items_page    

def get_invoice(pk):
    try:
        invoice = Invoice.objects.get(pk=pk)
        # Utilisez le related_name "articles" ou article_set si aucun related_name n'est défini
        items = invoice.articles.all()  # Remplacez "articles" par le related_name défini dans le modèle Article
    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found.", status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=400)

    context = {
        'obj': invoice,
        'articles': items
    }
    return context # Remplacez 'invoice_template.html' par le nom réel de votre template
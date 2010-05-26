from store.models import Transaction, Creator, Product
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from datetime import date, timedelta

@login_required
def front(request):
    # flatpage?
    pass

@login_required
def creators(request):
    creators = Creator.objects.all()
    return render_to_response('store/ledger/creator_list.html', context_instance = RequestContext(request, {'creators': creators}))

@login_required
def products(request):
    products = Product.objects.all()
    return render_to_response('store/ledger/product_list.html', context_instance = Requestcontext(request, {'creators': creators}))

@login_required
def filter_ledger(request, filter_by = None, filter = None, type = 'all'):
    # Get info from query string
    start = request.GET.get('startdate', None)
    duration = request.GET.get('duration', 'month')
    format = request.GET.get('format', 'html')
    depth = request.GET.get('depth', 'summary')

    #TODO: deal with type

    # Check permissions
    if depth == 'clean' and not (request.user.is_staff or request.user.is_superuser or request.user.creator_set.count()):
        request.user.message_set.create('You must be at least a staff member or a content creator to view this depth.')
        return render_to_response('store/ledger/permission_denied.html', context_instance = RequestContext(request))
    if depth == 'full' and not (request.user.is_staff or request.user.is_superuser):
        request.user.message_set.create('You must be a staff member to view this depth.')
        return render_to_response('store/ledger/permission_denied.html', context_instance = RequestContext(request))

    # default to today if day is not specified
    if start is not None:
        start = date(start.split('-'))
    else:
        start = date.today()

    # Set our durations
    end = start
    if duration == 'week':
        # week: start on a monday, end on a sunday
        start = start - timedelta(days = start.weekday())
        end = start + timedelta(days = 6)
    elif duration == 'month':
        # month: start on the first, end on the last day
        start = date(start.year, start.month, 1)
        end = date(start.year, start.month + 1, 1) - timedelta(days = 1)
    elif duration == 'quarter':
        # quarter: start on the first day of the quarter, end on the last
        if start.month in (1, 2, 3):
            start = date(start.year, 1, 1)
            end = date(start.year, 4, 1) - timedelta(days = 1)
        elif start.month in (4, 5, 6):
            start = date(start.year, 4, 1)
            end = date(start.year, 7, 1) - timedelta(days = 1)
        elif start.month in (7, 8, 9):
            start = date(start.year, 7, 1)
            end = date(start.year, 10, 1) - timedelta(days = 1)
        else:
            start = date(start.year, 10, 1)
            end = date(start.year + 1, 1, 1) - timedelta(days = 1)
    elif duration == 'year':
        start = date(start.year, 1, 1)
        end = date(start.year + 1, 1, 1) - timedelta(days = 1)
    elif duration == 'all':
        start = date.min
        end = date.today()
    assert start < end, "start date cannot be after end date."

    # Get the transaction set
    transaction_set = Transaction.objects.filter(**{str(filter_by): str(filter)}).filter(date__gte = start).filter(date__lte = end)

    # Build the summary
    summary = {}
    summary['count'] = transaction_set.count()
    summary['start'] = start
    summary['end'] = end
    summary['duration'] = duration
    summary['depth'] = depth
    summary['filter_by'] = filter_by
    summary['filter'] = filter
    for t in transaction_set:
        summary['total'] += t.amount
        summary[t.type] += 1
        summary[t.type]['total'] += t.amount

    # Finally, render
    return {'html': render_to_response('store/ledger/ledger_%s.html' % depth, context_instance = RequestContext(request, {'summary': summary, 'transaction_set': transaction_set})),
            'latex': render_to_response('store/ledger/ledger_%s.tex' % depth, context_instance = RequestContext(request, {'summary': summary, 'transaction_set': transaction_set})),
            'csv': generate_csv(depth, transaction_set, summary),
            'csv-excel': generate_csv(depth, transaction_set, summary, excel = True)}[format]

def generate_csv(depth, transaction_set, summary, excel = False):
    # Initiate
    from django.http import HttpResponse
    import csv
    writer = None
    response = HttpResponse(mimetype = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=ledger-%s-%s-%s.csv' % (summary['depth'], summary['duration'], summary['start'].toordinal())
    if excel:
        writer = csv.writer(response, dialect='excel')
    else:
        writer = csv.writer(response)

    # write at least the summary XXX: I hope this works...
    writer.writerows(summary)

    # chose according to depth what else should be written
    if depth == 'summary':
        return response
    elif depth == 'clean':
        writer.writerow(['Transaction ID', 'Transaction Date', 'Transaction Type', 'Transaction Amount'])
        for t in transaction_set:
            writer.writerow([t.id, t.date.isoformat(), t.get_type_display(), t.amount])
        return response
    elif depth == 'full':
        writer.writerow(['Transaction ID', 'Transaction Date', 'Transaction Type', 'Transaction Amount', 'Transaction Description', 'Cart ID', 'Cart Contents (if applicable)'])
        for t in transaction_set:
            writer.writerow([t.id, t.date.isoformat(), t.get_type_display(), t.amount, t.description, t.cart and t.cart.id or 'N/A', t.cart and t.cart.list_products() or 'N/A'])
        return response

def _days_in_february(year):
    #TODO: do we even need this?
    try:
        check = date(year, 2, 29)
    except ValueError:
        return 28
    return 29


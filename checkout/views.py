from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from manage_product.models import Product
from django.contrib import messages
from django.conf import settings
import stripe
from django.contrib.sites.models import Site
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    cart = request.session.get('cart', {})

    line_items = []

    for id, item in cart.items():
        product_object = get_object_or_404(Product, pk=id)

        line_items.append({
            'name': product_object.name,
            'price_in_cents': int(product_object.price * 100),
            'currency': 'sgd',
            'quantity': item['quantity']
        })

    current_site = Site.objects.get_current()
    domain = current_site.domain

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        success_url=domain + reverse(checkout_success),
        cancel_url=domain + reverse(checkout_cancelled)
    )

    context = {
        'session_id': session.id,
        'public_key': settings.STRIPE_PUBLISHABLE_KEY
    }

    return render(request, 'checkout/checkout.template.html', context)


def checkout_success(request):
    return HttpResponse('Checkout Success')


def checkout_cancelled(request):
    return HttpResponse('Checkout Cancelled')


@csrf_exempt
def payment_completed(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

    except ValueError as e:
        # invalid payload
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # invalid signature
        return HttpResponse(status=400)

    # handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # fulfill purchase
        handle_checkout_session(session)

    return HttpResponse(status=200)

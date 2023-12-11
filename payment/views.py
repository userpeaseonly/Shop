from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, reverse

from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    print("-------------------------------Payment Process-----------------------------------")
    print(order.first_name)
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        line_items = [
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Product Name',  # Replace with your product name
                    },
                    'unit_amount': int(order.get_total_cost() * 100),  # Total amount in cents
                },
                'quantity': 1,  # Quantity of the product
            }
            # Add more line items if needed for other products
        ]

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'payment_method_types': ['card'],
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': line_items  # Include line_items here
        }

        # Stripe coupon
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                name=order.coupon.code,
                percent_off=order.discount,
                duration='once')
            session_data['discounts'] = [{
                'coupon': stripe_coupon.id
            }]
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)
    print(locals())
    return render(request, 'payment/process.html', locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')

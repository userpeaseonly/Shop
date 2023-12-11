import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from .tasks import payment_completed


@csrf_exempt
def stripe_webhook(request):
    print("webhook called")
    try:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload=payload, sig_header=sig_header, secret_key=settings.STRIPE_WEBHOOK_SECRET_KEY)
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        if event.type == 'checkout.session.completed':
            session = event.data.object
            if session.mode == 'payment' and session.payment_status == 'paid':
                try:
                    order = Order.objects.get(id=session.client_reference_id)
                except Order.DoesNotExist:
                    return HttpResponse(status=404)
                order.paid = True
                order.stripe_id = session.payment_intent
                print(session.payment_intent + "--------------------------------------------------------------------")
                order.save()
                payment_completed.delay(order.id)
        return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponse({"data": str(e)}, status=400)

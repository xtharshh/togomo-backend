from django.db.models import Count, Sum
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NegotiationRequest, Payment, Restaurant, Subscription, SupportTicket, WalletTransaction


class DashboardSummaryView(APIView):
    """Lightweight operations snapshot for admin and restaurant dashboards."""

    def get(self, request):
        active_subscriptions = Subscription.objects.filter(status="active")
        pending_support = SupportTicket.objects.filter(status__in=["open", "in_progress"])
        open_negotiations = NegotiationRequest.objects.filter(status="open")
        paid_payments = Payment.objects.filter(status="paid")

        summary = {
            "active_subscribers": active_subscriptions.count(),
            "restaurants": Restaurant.objects.count(),
            "open_negotiations": open_negotiations.count(),
            "pending_support_tickets": pending_support.count(),
            "mrr": float(active_subscriptions.aggregate(total=Sum("negotiated_price"))['total'] or 0),
            "paid_payments_value": float(paid_payments.aggregate(total=Sum("amount"))['total'] or 0),
            "wallet_balance_total": float(WalletTransaction.objects.aggregate(total=Sum("amount"))['total'] or 0),
            "snapshot_date": now().date().isoformat(),
            "renewal_rate_hint": 0,
        }
        return Response(summary)

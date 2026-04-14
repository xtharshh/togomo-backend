from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.marketplace.models import (
    Address,
    AnalyticsSnapshot,
    Campaign,
    CommissionRule,
    Coupon,
    DeliveryAgent,
    DeliveryTask,
    MealPlan,
    MenuItem,
    NegotiationOffer,
    NegotiationRequest,
    NotificationLog,
    Payment,
    Review,
    Restaurant,
    RestaurantBranch,
    Settlement,
    SupportTicket,
    Subscription,
    SubscriptionDay,
    UserProfile,
    WalletTransaction,
)


class Command(BaseCommand):
    help = "Seed Togomo demo data for local development."

    def handle(self, *args, **options):
        User = get_user_model()

        customer, _ = User.objects.get_or_create(username="customer", defaults={"email": "customer@togomo.local"})
        customer.set_password("customer123")
        customer.save()

        owner, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@togomo.local"})
        owner.set_password("owner123")
        owner.save()

        rider, _ = User.objects.get_or_create(username="rider", defaults={"email": "rider@togomo.local"})
        rider.set_password("rider123")
        rider.save()

        admin_user, _ = User.objects.get_or_create(username="adminops", defaults={"email": "admin@togomo.local", "is_staff": True, "is_superuser": True})
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("admin123")
        admin_user.save()

        UserProfile.objects.get_or_create(user=customer, defaults={"role": "customer", "phone_number": "9000000001", "loyalty_points": 240})
        UserProfile.objects.get_or_create(user=owner, defaults={"role": "restaurant_owner", "phone_number": "9000000002"})
        UserProfile.objects.get_or_create(user=rider, defaults={"role": "delivery_agent", "phone_number": "9000000003"})
        UserProfile.objects.get_or_create(user=admin_user, defaults={"role": "admin", "phone_number": "9000000004"})

        restaurant, _ = Restaurant.objects.get_or_create(
            name="Togomo Kitchen Collective",
            defaults={
                "owner": owner,
                "description": "Premium tiffin service with rotating regional menus.",
                "cuisine_tags": "North Indian, South Indian, Jain, High Protein",
                "hygiene_score": Decimal("4.8"),
                "is_verified": True,
            },
        )

        branch, _ = RestaurantBranch.objects.get_or_create(
            restaurant=restaurant,
            name="Koramangala Central Kitchen",
            defaults={
                "address": "12th Main, Koramangala",
                "city": "Bengaluru",
                "postal_code": "560034",
                "service_radius_km": Decimal("8.5"),
            },
        )

        menu_items = []
        for name, price, diet_type in [
            ("Masala Khichdi Bowl", Decimal("129.00"), "veg"),
            ("Paneer Millet Lunch", Decimal("159.00"), "high_protein"),
            ("Jain Thali", Decimal("149.00"), "jain"),
        ]:
            menu_items.append(
                MenuItem.objects.get_or_create(
                    restaurant=restaurant,
                    name=name,
                    defaults={"price": price, "diet_type": diet_type, "description": "Chef curated daily meal."},
                )[0]
            )

        plan, _ = MealPlan.objects.get_or_create(
            restaurant=restaurant,
            title="Monthly Premium Plan",
            defaults={
                "description": "A premium recurring meal calendar for busy professionals.",
                "plan_type": "monthly",
                "price": Decimal("2499.00"),
                "meals_per_cycle": 30,
                "is_active": True,
            },
        )

        address, _ = Address.objects.get_or_create(
            user=customer,
            address_type="home",
            defaults={
                "line1": "101 Green Residency",
                "line2": "Near Silk Board",
                "city": "Bengaluru",
                "state": "Karnataka",
                "postal_code": "560068",
                "is_default": True,
            },
        )

        subscription, _ = Subscription.objects.get_or_create(
            user=customer,
            plan=plan,
            delivery_address=address,
            defaults={
                "start_date": timezone.now().date(),
                "status": "active",
                "negotiated_price": Decimal("2299.00"),
            },
        )

        day, _ = SubscriptionDay.objects.get_or_create(
            subscription=subscription,
            date=timezone.now().date(),
            defaults={"notes": "Leave at reception", "status": "scheduled"},
        )
        day.menu_items.set(menu_items[:2])

        NegotiationRequest.objects.get_or_create(
            user=customer,
            plan=plan,
            defaults={
                "offered_price": Decimal("2199.00"),
                "requested_duration_days": 30,
                "requested_meal_count": 30,
                "custom_notes": "Need low spice and one Jain day every week.",
                "status": "accepted",
            },
        )

        NegotiationOffer.objects.get_or_create(
            request=NegotiationRequest.objects.first(),
            proposed_by=owner,
            defaults={"amount": Decimal("2299.00"), "notes": "Approved with complimentary salad twice weekly.", "is_final": True},
        )

        agent, _ = DeliveryAgent.objects.get_or_create(
            user=rider,
            restaurant=restaurant,
            defaults={"vehicle_type": "scooter", "is_active": True},
        )

        DeliveryTask.objects.get_or_create(
            subscription_day=day,
            defaults={"agent": agent, "status": "out_for_delivery", "eta_minutes": 18, "otp": "1234"},
        )

        Payment.objects.get_or_create(
            subscription=subscription,
            defaults={"amount": Decimal("2299.00"), "status": "paid", "provider": "razorpay", "provider_reference": "pay_demo_001"},
        )

        WalletTransaction.objects.get_or_create(
            user=customer,
            amount=Decimal("250.00"),
            transaction_type="credit",
            reason="Welcome cashback",
        )

        Coupon.objects.get_or_create(
            code="TOGOMO50",
            defaults={"description": "Launch discount", "discount_amount": Decimal("50.00"), "minimum_order_value": Decimal("500.00"), "is_active": True},
        )

        Review.objects.get_or_create(
            user=customer,
            restaurant=restaurant,
            defaults={"rating": 5, "comment": "Premium packaging and reliable delivery.", "is_verified_purchase": True},
        )

        SupportTicket.objects.get_or_create(
            user=customer,
            title="Need extra salad on Thursdays",
            defaults={"description": "Please add salad to Thursday lunch meals.", "status": "open", "reference_code": "SUP-001"},
        )

        NotificationLog.objects.get_or_create(
            user=customer,
            channel="push",
            title="Your tiffin is on the way",
            defaults={"body": "Your rider has picked up today's meal."},
        )

        CommissionRule.objects.get_or_create(
            city="Bengaluru",
            vendor_type="restaurant",
            plan_type="monthly",
            defaults={"commission_percent": Decimal("12.00"), "flat_fee": Decimal("0.00"), "is_active": True},
        )

        Settlement.objects.get_or_create(
            restaurant=restaurant,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            defaults={"gross_amount": Decimal("2299.00"), "commission_amount": Decimal("275.88"), "net_amount": Decimal("2023.12"), "status": "pending"},
        )

        AnalyticsSnapshot.objects.get_or_create(
            scope="city:bengaluru",
            metric_name="active_subscribers",
            defaults={"metric_value": Decimal("128.00")},
        )

        Campaign.objects.get_or_create(
            name="Festival Lunch Push",
            defaults={"channel": "push", "message": "Try the festive lunch pack today.", "is_active": True},
        )

        self.stdout.write(self.style.SUCCESS("Seeded Togomo demo data successfully."))

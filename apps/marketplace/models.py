from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(TimeStampedModel):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("restaurant_owner", "Restaurant Owner"),
        ("staff", "Staff"),
        ("delivery_agent", "Delivery Agent"),
        ("admin", "Admin"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default="customer")
    phone_number = models.CharField(max_length=20, blank=True)
    referral_code = models.CharField(max_length=40, blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.user} - {self.role}"


class Address(TimeStampedModel):
    ADDRESS_TYPE_CHOICES = [
        ("home", "Home"),
        ("office", "Office"),
        ("hostel", "Hostel"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default="home")
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} - {self.address_type}"


class Restaurant(TimeStampedModel):
    name = models.CharField(max_length=180)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_restaurants")
    description = models.TextField(blank=True)
    cuisine_tags = models.CharField(max_length=255, blank=True)
    hygiene_score = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class RestaurantBranch(TimeStampedModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=180)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    postal_code = models.CharField(max_length=20)
    service_radius_km = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)

    def __str__(self) -> str:
        return f"{self.restaurant.name} - {self.name}"


class MenuItem(TimeStampedModel):
    DIET_CHOICES = [
        ("veg", "Vegetarian"),
        ("non_veg", "Non Vegetarian"),
        ("jain", "Jain"),
        ("high_protein", "High Protein"),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES, default="veg")
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.restaurant.name} - {self.name}"


class MealPlan(TimeStampedModel):
    PLAN_TYPE_CHOICES = [
        ("per_day", "Per Day"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("trial", "Trial"),
        ("custom", "Custom"),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="meal_plans")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default="monthly")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    meals_per_cycle = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.restaurant.name} - {self.title}"


class Subscription(TimeStampedModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("paused", "Paused"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(MealPlan, on_delete=models.PROTECT, related_name="subscriptions")
    delivery_address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    negotiated_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.plan.title}"


class SubscriptionDay(TimeStampedModel):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("skipped", "Skipped"),
        ("prepared", "Prepared"),
        ("delivered", "Delivered"),
        ("issue_reported", "Issue Reported"),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="days")
    date = models.DateField()
    menu_items = models.ManyToManyField(MenuItem, blank=True, related_name="subscription_days")
    notes = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")

    class Meta:
        unique_together = ("subscription", "date")

    def __str__(self) -> str:
        return f"{self.subscription} - {self.date}"


class NegotiationRequest(TimeStampedModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="negotiation_requests")
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="negotiation_requests")
    offered_price = models.DecimalField(max_digits=10, decimal_places=2)
    requested_duration_days = models.PositiveIntegerField(default=30)
    requested_meal_count = models.PositiveIntegerField(default=30)
    custom_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")

    def __str__(self) -> str:
        return f"Negotiation {self.id} - {self.user}"


class NegotiationOffer(TimeStampedModel):
    request = models.ForeignKey(NegotiationRequest, on_delete=models.CASCADE, related_name="offers")
    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="negotiation_offers")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    is_final = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Offer {self.id} for request {self.request_id}"


class DeliveryAgent(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="delivery_agent_profile")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="delivery_agents")
    vehicle_type = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user} ({self.restaurant.name})"


class DeliveryTask(TimeStampedModel):
    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("picked_up", "Picked Up"),
        ("out_for_delivery", "Out For Delivery"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ]

    subscription_day = models.ForeignKey(SubscriptionDay, on_delete=models.CASCADE, related_name="delivery_tasks")
    agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="assigned")
    eta_minutes = models.PositiveIntegerField(default=30)
    otp = models.CharField(max_length=10, blank=True)

    def __str__(self) -> str:
        return f"Task {self.id} - {self.status}"


class Payment(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    provider = models.CharField(max_length=50, default="razorpay")
    provider_reference = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"Payment {self.id} - {self.status}"


class WalletTransaction(TimeStampedModel):
    TYPE_CHOICES = [
        ("credit", "Credit"),
        ("debit", "Debit"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.user} - {self.transaction_type} {self.amount}"


class Coupon(TimeStampedModel):
    code = models.CharField(max_length=40, unique=True)
    description = models.TextField(blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.code


class Review(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.restaurant.name} - {self.rating}"


class SupportTicket(TimeStampedModel):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="support_tickets")
    title = models.CharField(max_length=180)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    reference_code = models.CharField(max_length=40, blank=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"


class NotificationLog(TimeStampedModel):
    CHANNEL_CHOICES = [
        ("push", "Push"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("in_app", "In App"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="in_app")
    title = models.CharField(max_length=180)
    body = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user} - {self.title}"


class CommissionRule(TimeStampedModel):
    city = models.CharField(max_length=120, blank=True)
    vendor_type = models.CharField(max_length=80, blank=True)
    plan_type = models.CharField(max_length=20, blank=True)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    flat_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        scope = self.city or self.vendor_type or self.plan_type or "global"
        return f"{scope} commission"


class Settlement(TimeStampedModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="settlements")
    period_start = models.DateField()
    period_end = models.DateField()
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self) -> str:
        return f"{self.restaurant.name} {self.period_start} - {self.period_end}"


class AnalyticsSnapshot(TimeStampedModel):
    scope = models.CharField(max_length=120, blank=True)
    metric_name = models.CharField(max_length=120)
    metric_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    captured_on = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.metric_name}: {self.metric_value}"


class CouponRedemption(TimeStampedModel):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="redemptions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_redemptions")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="coupon_redemptions")
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.coupon.code} - {self.user}"


class Campaign(TimeStampedModel):
    CHANNEL_CHOICES = [
        ("push", "Push"),
        ("sms", "SMS"),
        ("whatsapp", "WhatsApp"),
        ("email", "Email"),
        ("in_app", "In App"),
    ]

    name = models.CharField(max_length=180)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default="push")
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

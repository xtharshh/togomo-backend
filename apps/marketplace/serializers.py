from rest_framework import serializers

from .models import (
    Address,
    AnalyticsSnapshot,
    Campaign,
    CommissionRule,
    CouponRedemption,
    DeliveryTask,
    NotificationLog,
    MealPlan,
    Coupon,
    NegotiationRequest,
    Review,
    Restaurant,
    SupportTicket,
    Subscription,
    SubscriptionDay,
    UserProfile,
    Settlement,
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"


class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class CommissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRule
        fields = "__all__"


class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = "__all__"


class AnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsSnapshot
        fields = "__all__"


class CouponRedemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CouponRedemption
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"


class SubscriptionDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDay
        fields = "__all__"


class NegotiationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRequest
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = "__all__"


class DeliveryTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTask
        fields = "__all__"


class NotificationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationLog
        fields = "__all__"


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = "__all__"

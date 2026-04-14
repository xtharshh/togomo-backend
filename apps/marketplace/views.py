from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from .models import (
    Address,
    AnalyticsSnapshot,
    Campaign,
    CommissionRule,
    CouponRedemption,
    DeliveryTask,
    NotificationLog,
    Coupon,
    MealPlan,
    NegotiationRequest,
    Review,
    Restaurant,
    SupportTicket,
    Subscription,
    SubscriptionDay,
    UserProfile,
    Settlement,
)
from .serializers import (
    AddressSerializer,
    AnalyticsSnapshotSerializer,
    CampaignSerializer,
    CommissionRuleSerializer,
    CouponRedemptionSerializer,
    DeliveryTaskSerializer,
    NotificationLogSerializer,
    CouponSerializer,
    MealPlanSerializer,
    NegotiationRequestSerializer,
    ReviewSerializer,
    RestaurantSerializer,
    SupportTicketSerializer,
    SubscriptionDaySerializer,
    SubscriptionSerializer,
    UserProfileSerializer,
    SettlementSerializer,
)
from .permissions import (
    HasMarketplaceRole,
    IsAdminRole,
    IsCustomerRole,
    IsDeliveryAgentOrAdmin,
    IsRestaurantOwnerOrAdmin,
)


class RoleFilteredViewSet(viewsets.ModelViewSet):
    permission_classes = [HasMarketplaceRole]
    owner_filter_field = None
    self_only = False

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)

        if not user.is_authenticated:
            return queryset.none()

        if role == "admin":
            return queryset

        if self.self_only:
            return queryset.filter(user=user)

        if self.owner_filter_field:
            return queryset.filter(**{self.owner_filter_field: user})

        return queryset.filter(user=user)


class AdminOnlyViewSet(RoleFilteredViewSet):
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        profile = getattr(self.request.user, "profile", None)
        if getattr(profile, "role", None) != "admin":
            return super().get_queryset().none()
        return super().get_queryset()


class RestaurantOwnerViewSet(RoleFilteredViewSet):
    permission_classes = [IsRestaurantOwnerOrAdmin]


class CustomerViewSet(RoleFilteredViewSet):
    permission_classes = [IsCustomerRole]


class DeliveryAgentViewSet(RoleFilteredViewSet):
    permission_classes = [IsDeliveryAgentOrAdmin]


class AddressViewSet(CustomerViewSet):
    queryset = Address.objects.select_related("user").all().order_by("-created_at")
    serializer_class = AddressSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserProfileViewSet(RoleFilteredViewSet):
    queryset = UserProfile.objects.select_related("user").all().order_by("-created_at")
    serializer_class = UserProfileSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RestaurantViewSet(RestaurantOwnerViewSet):
    queryset = Restaurant.objects.select_related("owner").all().order_by("name")
    serializer_class = RestaurantSerializer
    owner_filter_field = "owner"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MealPlanViewSet(RestaurantOwnerViewSet):
    queryset = MealPlan.objects.select_related("restaurant").all().order_by("title")
    serializer_class = MealPlanSerializer
    owner_filter_field = "restaurant__owner"

    def perform_create(self, serializer):
        restaurant = serializer.validated_data.get("restaurant")
        if getattr(self.request.user.profile, "role", None) != "admin" and restaurant.owner != self.request.user:
            raise PermissionDenied("You can only create plans for your own restaurant.")
        serializer.save()


class CouponViewSet(AdminOnlyViewSet):
    queryset = Coupon.objects.all().order_by("-created_at")
    serializer_class = CouponSerializer


class CommissionRuleViewSet(AdminOnlyViewSet):
    queryset = CommissionRule.objects.all().order_by("-created_at")
    serializer_class = CommissionRuleSerializer


class SettlementViewSet(AdminOnlyViewSet):
    queryset = Settlement.objects.select_related("restaurant").all().order_by("-created_at")
    serializer_class = SettlementSerializer


class AnalyticsSnapshotViewSet(AdminOnlyViewSet):
    queryset = AnalyticsSnapshot.objects.all().order_by("-captured_on", "-created_at")
    serializer_class = AnalyticsSnapshotSerializer


class CouponRedemptionViewSet(CustomerViewSet):
    queryset = CouponRedemption.objects.select_related("coupon", "user", "subscription").all().order_by("-redeemed_at")
    serializer_class = CouponRedemptionSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionViewSet(CustomerViewSet):
    queryset = Subscription.objects.select_related("user", "plan", "delivery_address").all().order_by("-created_at")
    serializer_class = SubscriptionSerializer
    self_only = True

    def perform_create(self, serializer):
        delivery_address = serializer.validated_data.get("delivery_address")
        if delivery_address.user != self.request.user:
            raise PermissionDenied("You can only subscribe with your own address.")
        serializer.save(user=self.request.user)


class SubscriptionDayViewSet(CustomerViewSet):
    queryset = SubscriptionDay.objects.select_related("subscription").prefetch_related("menu_items").all().order_by("-date")
    serializer_class = SubscriptionDaySerializer
    self_only = True

    def get_queryset(self):
        queryset = SubscriptionDay.objects.select_related("subscription").prefetch_related("menu_items").all().order_by("-date")
        user = self.request.user
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)

        if not user.is_authenticated:
            return queryset.none()
        if role == "admin":
            return queryset
        return queryset.filter(subscription__user=user)


class NegotiationRequestViewSet(CustomerViewSet):
    queryset = NegotiationRequest.objects.select_related("user", "plan").all().order_by("-created_at")
    serializer_class = NegotiationRequestSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(CustomerViewSet):
    queryset = Review.objects.select_related("user", "restaurant").all().order_by("-created_at")
    serializer_class = ReviewSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SupportTicketViewSet(CustomerViewSet):
    queryset = SupportTicket.objects.select_related("user").all().order_by("-created_at")
    serializer_class = SupportTicketSerializer
    self_only = True

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DeliveryTaskViewSet(DeliveryAgentViewSet):
    queryset = DeliveryTask.objects.select_related("subscription_day", "agent").all().order_by("-created_at")
    serializer_class = DeliveryTaskSerializer
    self_only = True

    def get_queryset(self):
        queryset = DeliveryTask.objects.select_related("subscription_day", "agent").all().order_by("-created_at")
        user = self.request.user
        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)

        if not user.is_authenticated:
            return queryset.none()
        if role == "admin":
            return queryset
        return queryset.filter(agent__user=user)


class NotificationLogViewSet(CustomerViewSet):
    queryset = NotificationLog.objects.select_related("user").all().order_by("-created_at")
    serializer_class = NotificationLogSerializer
    self_only = True


class CampaignViewSet(AdminOnlyViewSet):
    queryset = Campaign.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer

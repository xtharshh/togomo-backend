from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .auth_views import LoginView, LogoutView, MeView, RegisterView
from .dashboard import DashboardSummaryView
from .views import (
    AddressViewSet,
    AnalyticsSnapshotViewSet,
    CampaignViewSet,
    CommissionRuleViewSet,
    CouponRedemptionViewSet,
    DeliveryTaskViewSet,
    NotificationLogViewSet,
    CouponViewSet,
    MealPlanViewSet,
    NegotiationRequestViewSet,
    ReviewViewSet,
    RestaurantViewSet,
    SupportTicketViewSet,
    SubscriptionDayViewSet,
    SubscriptionViewSet,
    UserProfileViewSet,
    SettlementViewSet,
)

router = DefaultRouter()
router.register("profiles", UserProfileViewSet)
router.register("addresses", AddressViewSet)
router.register("restaurants", RestaurantViewSet)
router.register("meal-plans", MealPlanViewSet)
router.register("coupons", CouponViewSet)
router.register("commission-rules", CommissionRuleViewSet)
router.register("settlements", SettlementViewSet)
router.register("analytics", AnalyticsSnapshotViewSet)
router.register("coupon-redemptions", CouponRedemptionViewSet)
router.register("subscriptions", SubscriptionViewSet)
router.register("subscription-days", SubscriptionDayViewSet)
router.register("negotiation-requests", NegotiationRequestViewSet)
router.register("reviews", ReviewViewSet)
router.register("support-tickets", SupportTicketViewSet)
router.register("delivery-tasks", DeliveryTaskViewSet)
router.register("notifications", NotificationLogViewSet)
router.register("campaigns", CampaignViewSet)

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("", include(router.urls)),
    path("dashboard-summary/", DashboardSummaryView.as_view()),
]

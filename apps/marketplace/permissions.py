from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(getattr(request.user, 'profile', None), 'role', None) == 'admin')


class HasMarketplaceRole(BasePermission):
    allowed_roles = {'customer', 'restaurant_owner', 'staff', 'delivery_agent', 'admin'}

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in self.allowed_roles


class IsCustomerRole(BasePermission):
    allowed_roles = {'customer', 'admin'}

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in self.allowed_roles


class IsRestaurantOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in {'restaurant_owner', 'admin'}


class IsDeliveryAgentOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = getattr(getattr(request.user, 'profile', None), 'role', None)
        return role in {'delivery_agent', 'admin'}


class ReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and getattr(getattr(request.user, 'profile', None), 'role', None) == 'admin')

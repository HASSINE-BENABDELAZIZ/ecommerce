from rest_framework.permissions import BasePermission


class CanViewOrder(BasePermission):

    def has_permission(self, request, view):
        if "orders.view_order" in request.user.get_all_permissions():
            return True

        return False


class CanViewOrderItems(BasePermission):

    def has_permission(self, request, view):
        if "orders.view_orderitems" in request.user.get_all_permissions():
            return True

        return False


class CanViewShipment(BasePermission):

    def has_permission(self, request, view):
        if "orders.view_shipment" in request.user.get_all_permissions():
            return True

        return False


class CanViewProduct(BasePermission):

    def has_permission(self, request, view):
        if "products.view_product" in request.user.get_all_permissions():
            return True

        return False


class CanEditOrder(BasePermission):

    def has_permission(self, request, view):
        if "orders.change_order" in request.user.get_all_permissions():
            return True

        return False


class CanEditOrderItems(BasePermission):

    def has_permission(self, request, view):
        if "orders.change_orderitems" in request.user.get_all_permissions():
            return True

        return False


class CanEditShipment(BasePermission):

    def has_permission(self, request, view):
        if "orders.change_shipment" in request.user.get_all_permissions():
            return True

        return False


class CanEditProduct(BasePermission):

    def has_permission(self, request, view):
        if "personnel" in request.user.groups.all():
            return True

        return False

from rest_framework import permissions

# permisions
# is order costumer permissions
class IsOrderCostumerOrReadOnly(permissions.BasePermission):
    message = "This user is not costumer of this order"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            return request.user.is_authenticated

        obj = view.get_object()
        user = request.user

        return user == obj.costumer


# is executor user
class IsExecutorOrReadOnly(permissions.BasePermission):
    message = 'This user is not executor'

    def has_permission(self, request, view):
        obj = view.get_object()
        if request.method == 'POST':
            return request.user.is_authenticated and request.user.is_executor
        elif request.method == 'PUT':
            return request.user == obj.order.costumer

        return True
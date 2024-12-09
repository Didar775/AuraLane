from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from .models import Cart, Order
from catalog.models import Item


class CartOrderView(View):

    def get_order_for_user(self, request):
        """Retrieve or create an order for the current user or session."""
        if request.user.is_authenticated:
            # Fetch or create an order for authenticated users
            order, _ = Order.objects.get_or_create(user=request.user, status="new")
        else:
            # For anonymous users, use the session
            order_id = request.session.get("order_id")
            if order_id:
                order = get_object_or_404(Order, id=order_id, status="new")
            else:
                order = Order.objects.create(status="new")
                request.session["order_id"] = order.id
        return order

    def get(self, request):
        """List all active carts and their associated order."""
        order = self.get_order_for_user(request)
        carts = order.carts.all()

        return render(request, "sales/cart.html", {"carts": carts, "order": order})

    def post(self, request):
        action = request.POST.get("action")
        item_id = request.POST.get("item_id")
        cart_id = request.POST.get("cart_id")

        # Retrieve the active order
        order = self.get_order_for_user(request)

        if action == "add":  # Add a new item to the cart
            if not item_id:
                return HttpResponseBadRequest("Item ID is required.")
            item = get_object_or_404(Item, id=item_id)
            cart, created = Cart.objects.get_or_create(item=item, order=order)
            if not created:
                cart.quantity += 1  # Increment quantity if the item is already in the cart
                cart.save()
            return JsonResponse({"message": "Item added to cart."}, status=201)

        elif action in ["increase", "decrease"]:  # Update the quantity of a cart item
            if not cart_id:
                return HttpResponseBadRequest("Cart ID is required.")
            cart = get_object_or_404(Cart, id=cart_id, order=order)

            if action == "increase":
                cart.quantity += 1
            elif action == "decrease" and cart.quantity > 1:
                cart.quantity -= 1

            cart.save()
            return redirect("sales:cart_order")

        return HttpResponseBadRequest("Invalid action.")

    def delete(self, request, cart_id=None):
        if not cart_id:
            return HttpResponseBadRequest("Cart ID is required.")

        # Retrieve the active order
        order = self.get_order_for_user(request)
        cart = get_object_or_404(Cart, id=cart_id, order=order)

        # Remove the cart item
        cart.delete()

        # If the order has no more carts, mark it as canceled
        if not order.carts.exists():
            order.status = "canceled"
            order.save()

        return JsonResponse({"message": "Item removed from cart."}, status=204)

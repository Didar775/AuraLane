import json

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from .models import Cart, Order
from catalog.models import Item
from django.contrib.auth import get_user_model

User = get_user_model()


class CartOrderView(View):
    def get_user_from_token(self, request):
        """
        Extract and authenticate the user from the access token in cookies.
        Refresh the access token if expired using the refresh token.
        """
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token:
            if refresh_token:
                try:
                    refresh = RefreshToken(refresh_token)
                    # Generate a new access token
                    new_access_token = str(refresh.access_token)

                    # Set the new access token in the response
                    self.response = JsonResponse({"message": "Token refreshed."})
                    self.response.set_cookie(
                        key="access_token",
                        value=new_access_token,
                        httponly=True,
                        secure=True,
                        samesite="Lax",
                        max_age=60 * 15  # 15 minutes
                    )
                    access_token = new_access_token
                except Exception:
                    raise AuthenticationFailed("Invalid or expired refresh token.")
            else:
                raise AuthenticationFailed("No tokens available for authentication.")

        try:
            # Decode and validate the access token
            token = AccessToken(access_token)
            user_id = token["user_id"]
        except Exception:
            raise AuthenticationFailed("Invalid or expired access token.")

        # Fetch the user instance
        return get_object_or_404(User, id=user_id)

    def get_order_for_user(self, request):
        """Retrieve or create an order for the current user or session."""
        user = self.get_user_from_token(request)
        if user.is_authenticated:
            # Fetch or create an order for authenticated users
            order, _ = Order.objects.get_or_create(user=user, status="new")
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
        try:
            order = self.get_order_for_user(request)
            carts = order.carts.all()
            return render(request, "sales/cart.html", {"carts": carts, "order": order})
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=401)

    def post(self, request):
        """Handle cart actions such as adding, increasing, or decreasing items."""
        try:
            user = self.get_user_from_token(request)
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=401)

        try:
            # Try parsing JSON payload
            data = json.loads(request.body)
            action = data.get("action")
            cart_id = data.get("cart_id")
            item_id = data.get("item_id")
        except json.JSONDecodeError:
            # If JSON parsing fails, fallback to form-encoded data
            action = request.POST.get("action")
            cart_id = request.POST.get("cart_id")
            item_id = request.POST.get("item_id")

        # Retrieve the active order
        order = self.get_order_for_user(request)
        print(action)
        print(item_id)
        print("Raw request body:", request.body)

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
            return JsonResponse({"message": "Cart updated.", "quantity": cart.quantity})

        return HttpResponseBadRequest("Invalid action.")

    def delete(self, request, cart_id=None):
        """Remove an item from the cart."""
        try:
            user = self.get_user_from_token(request)
        except AuthenticationFailed as e:
            return JsonResponse({"error": str(e)}, status=401)

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

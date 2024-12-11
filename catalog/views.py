from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Avg, Q
from django.http import JsonResponse, request, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from sales.models import Order, Cart
from .models import Item, Category, Review, FavoriteItem
from .forms import ItemForm, ReviewForm


def home_view(request):
    return render(request, 'home.html')


class ItemListView(ListView):
    model = Item
    template_name = 'catalog/catalog_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = Item.objects.filter(in_stock=True).prefetch_related('photos', 'ratings').select_related('category')

        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))

        queryset = queryset.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')

        cart_item_ids = self.get_cart_item_ids()
        for item in queryset:
            item.in_cart = item.id in cart_item_ids

        return queryset

    def get_cart_item_ids(self):
        if self.request.user.is_authenticated:
            order = Order.objects.filter(user=self.request.user, status="new").first()
        else:
            order_id = self.request.session.get("order_id")
            order = Order.objects.filter(id=order_id, status="new").first()

        if order:
            return order.carts.values_list('item_id', flat=True)
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.filter(archived=False)
        context['range'] = range(1, 6)
        context['query'] = self.request.GET.get('q', '')

        return context


class ItemDetailView(DetailView):
    model = Item
    template_name = 'catalog/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.ratings.all()
        context['review_form'] = ReviewForm()
        context['range'] = range(1, 6)

        related_items = Item.objects.filter(
            category=self.object.category,
            in_stock=True
        ).exclude(id=self.object.id)[:4]
        context['related_items'] = related_items

        return context


@login_required
def submit_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        print(request.POST)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.item = item
            review.save()
            return redirect('catalog:item_detail', pk=item_id)


@login_required
def toggle_favorite(request, product_id):
    if request.method == "POST":
        item = get_object_or_404(Item, id=product_id)
        user = request.user

        # Check if the favorite item exists
        favorite_item, created = FavoriteItem.objects.get_or_create(item=item, user=user)

        if not created:
            # If it already exists, remove it (toggle off)
            favorite_item.delete()
            is_favorite = False
        else:
            # If it doesn't exist, it has been added as a favorite
            is_favorite = True

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class FavoriteItemView(View):

    def get(self, request):
        """Retrieve all favorite items."""
        if request.user and not isinstance(request.user, AnonymousUser):
            favorite_items = FavoriteItem.objects.filter(user=request.user).select_related('item')
            context = {'favorite_items': favorite_items}
            return render(request, 'catalog/favorites.html', context)
        return render(request, 'catalog/favorites.html', {'favorite_items': []})

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You need to log in to modify favorites.")

        action = request.POST.get('action')
        item_id = request.POST.get('item_id')

        if not item_id:
            return HttpResponseBadRequest("Item ID is required.")

        item = get_object_or_404(Item, id=item_id)

        if action == 'add':
            _, created = FavoriteItem.objects.get_or_create(user=request.user, item=item)
            if created:
                return JsonResponse({"message": "Item added to favorites."}, status=201)
            return JsonResponse({"message": "Item is already in favorites."}, status=200)

        elif action == 'remove':
            favorite = FavoriteItem.objects.filter(user=request.user, item=item).first()
            if favorite:
                favorite.delete()
                return JsonResponse({"message": "Item removed from favorites."}, status=204)
            return JsonResponse({"error": "Favorite item not found."}, status=404)

        return HttpResponseBadRequest("Invalid action.")

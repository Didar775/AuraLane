from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Item, Category, Review, FavoriteItem
from .forms import ItemForm, ReviewForm


def home_view(request):
    return render(request, 'home.html')


from django.shortcuts import render, get_object_or_404
from .models import Category, Item


class CategoryListView(ListView):
    model = Category
    template_name = 'catalog/catalog_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(archived=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get('category_id')

        if category_id:
            context['items'] = Item.objects.filter(
                category_id=category_id,
                in_stock=True
            ).select_related('category')

        context['range'] = range(1, 6)

        return context


class ItemListView(ListView):
    model = Item
    template_name = 'catalog/items_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = Item.objects.filter(
            in_stock=True
        ).prefetch_related('photos').select_related('category')

        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

class ItemDetailView(DetailView):
    model = Item
    template_name = 'catalog/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(item=self.object)
        context['is_favorite'] = FavoriteItem.objects.filter(user=self.request.user, item=self.object).exists()
        return context



@csrf_exempt
def toggle_favorite(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(Item, id=product_id)
        user = request.user

        # Toggle favorite
        if product in user.profile.favorites.all():
            user.profile.favorites.remove(product)
            is_favorite = False
        else:
            user.profile.favorites.add(product)
            is_favorite = True

        return JsonResponse({'is_favorite': is_favorite})


@csrf_exempt
def toggle_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Item, id=product_id)
        user = request.user

        if product in user.profile.cart.all():
            user.profile.cart.remove(product)
            return JsonResponse({'is_in_cart': False})
        else:
            user.profile.cart.add(product)
            return JsonResponse({'is_in_cart': True})



@login_required
def submit_review(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.item = item
            review.save()
            return redirect('catalog:item_detail', pk=item_id)
    else:
        form = ReviewForm()
    return render(request, 'catalog/review_form.html', {'form': form, 'item': item})
# A static homepage

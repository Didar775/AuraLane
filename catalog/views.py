from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, request
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Item, Category, Review, FavoriteItem
from .forms import ItemForm, ReviewForm


def home_view(request):
    return render(request, 'home.html')


from django.shortcuts import render, get_object_or_404
from .models import Category, Item


def catalog_list(request):
    categories = Category.objects.all()
    category_id = request.GET.get('category_id')

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        items = category.items.all()
    else:
        items = Item.objects.all()

    context = {
        'categories': categories,
        'items': items,
    }
    return render(request, 'catalog/catalog_list.html', context)


def items_by_category(request, category_id):
    items = Item.objects.filter(category_id=category_id)
    items_data = [{
        'name': item.name,
        'price': item.sale_price,
        'image': item.photos.first().photo.url if item.photos.exists() else '',
    } for item in items]

    return JsonResponse({'items': items_data})


# ListView for Items
class ItemListView(ListView):
    model = Item
    template_name = 'catalog/item_list.html'
    context_object_name = 'items'
    paginate_by = 10


# DetailView for an Item
class ItemDetailView(DetailView):
    model = Item
    template_name = 'catalog/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(item=self.object)
        context['is_favorite'] = FavoriteItem.objects.filter(user=self.request.user, item=self.object).exists()
        return context


@login_required
def toggle_favorite(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    favorite, created = FavoriteItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        favorite.delete()
        return JsonResponse({'message': 'Removed from favorites'}, status=200)
    return JsonResponse({'message': 'Added to favorites'}, status=200)


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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile, Address
from .forms import UserProfileForm, AddressForm
from django.forms import modelformset_factory
import logging

@login_required
def profile_page(request):
    logging.error(f"User ID: {request.user.id}")

    # 👇 Создаём UserProfile, если он отсутствует
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if created:
        logging.info(f"✅ UserProfile created for user_id={request.user.id}")

    # 👇 Создаём AddressFormSet
    AddressFormSet = modelformset_factory(Address, form=AddressForm, extra=1, can_delete=True)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  # 👈 добавили request.FILES
        address_formset = AddressFormSet(request.POST, queryset=Address.objects.filter(user=request.user))

        if profile_form.is_valid() and address_formset.is_valid():
            profile_form.save()

            # Сохраняем адреса и привязываем их к текущему пользователю
            addresses = address_formset.save(commit=False)
            for address in addresses:
                address.user = request.user
                address.save()

            # Удаляем удалённые адреса
            for deleted_address in address_formset.deleted_objects:
                deleted_address.delete()

            return redirect('profile_page')

    else:
        profile_form = UserProfileForm(instance=user_profile)
        address_formset = AddressFormSet(queryset=Address.objects.filter(user=request.user))

    return render(request, 'profile_page.html', {
        'profile_form': profile_form,
        'address_formset': address_formset,
    })

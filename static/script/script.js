function toggleFavorite(button) {
    const heartIcon = button.querySelector('.heart-icon');
    heartIcon.classList.toggle('filled');
    if (heartIcon.classList.contains('filled')) {
        heartIcon.style.fill = '#713535';
        heartIcon.style.stroke = '#552323';
    } else {
        heartIcon.style.fill = 'none';
        heartIcon.style.stroke = '#333';
    }
}

function toggleCart(button) {
    button.classList.toggle('added');
    if (button.classList.contains('added')) {
        button.style.backgroundColor = '#713535';
        button.style.transform = 'scale(1.2)';
    } else {
        button.style.backgroundColor = '#333';
        button.style.transform = 'scale(1)';
    }
}

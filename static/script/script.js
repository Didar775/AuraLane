function isAuthenticated(callback) {
    fetch('/auth-check/') // Your Django authentication check endpoint
        .then(response => response.json())
        .then(data => {
            if (data.is_authenticated) {
                callback(); // Proceed with the original action
            } else {
                // Redirect to the login page with the current page as a 'next' parameter
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
            }
        })
        .catch(error => console.error('Error checking authentication:', error));
}

function toggleFavorite(button) {
    isAuthenticated(() => {
        const heartIcon = button.querySelector('.heart-icon');
        heartIcon.classList.toggle('filled');
        if (heartIcon.classList.contains('filled')) {
            heartIcon.style.fill = '#713535';
            heartIcon.style.stroke = '#552323';
        } else {
            heartIcon.style.fill = 'none';
            heartIcon.style.stroke = '#333';
        }

        // Example backend call to update favorite status
        const productId = button.getAttribute('data-product-id'); // Assuming data-product-id is set on the button
        fetch(`/toggle-favorite/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        }).catch(error => console.error('Error toggling favorite:', error));
    });
}

function toggleCart(button) {
    isAuthenticated(() => {
        button.classList.toggle('added');
        if (button.classList.contains('added')) {
            button.style.backgroundColor = '#713535';
            button.style.transform = 'scale(1.2)';
        } else {
            button.style.backgroundColor = '#333';
            button.style.transform = 'scale(1)';
        }

        // Example backend call to update cart status
        const productId = button.getAttribute('data-product-id'); // Assuming data-product-id is set on the button
        fetch(`/toggle-cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        }).catch(error => console.error('Error toggling cart:', error));
    });
}

// Utility function to get CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

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

async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        console.error('Refresh token is missing!');
        return null;
    }

    try {
        const response = await fetch('/api/auth/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // Include CSRF token if required
            },
            body: JSON.stringify({ refresh: refreshToken }) // Send the refresh token
        });

        if (!response.ok) {
            throw new Error('Failed to refresh access token');
        }

        const data = await response.json();
        const newAccessToken = data.access; // Assuming the new access token is in the "access" field

        // Store the new access token (e.g., in localStorage or cookies)
        document.cookie = `access_token=${newAccessToken}; path=/;`;

        return newAccessToken;
    } catch (error) {
        console.error('Error refreshing access token:', error);
        return null;
    }
}

function getRefreshToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'refresh_token') {
            return value;
        }
    }
    return null;
}



// Helper function to get the access token from cookies
async function getAccessToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'access_token') {
            return value; // Return the existing access token
        }
    }

    console.warn('Access token is missing! Attempting to refresh...');
    return await refreshAccessToken(); // Refresh the token if missing
}

async function toggleCart(button) {
    const itemId = button.getAttribute('data-item-id'); // Get the item ID
    const action = button.classList.contains('added') ? 'remove' : 'add'; // Determine the action

    try {
        const response = await fetch('/cart-order/', {
            method: 'POST',
            credentials: 'include', // Automatically include cookies
            headers: {
                'X-CSRFToken': getCSRFToken(), // Include CSRF token
                'Content-Type': 'application/json', // JSON Content-Type
            },
            body: JSON.stringify({ action: action, item_id: itemId }) // Send JSON payload
        });

        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }

        const data = await response.json();
        console.log('Cart updated:', data);

        // Update button appearance based on action
        if (action === 'add') {
            button.classList.add('added');
            button.style.backgroundColor = '#713535';
            button.style.transform = 'scale(1.2)';
        } else if (action === 'remove') {
            button.classList.remove('added');
            button.style.backgroundColor = '#333';
            button.style.transform = 'scale(1)';
        }
    } catch (error) {
        console.error('Error toggling cart:', error);
    }
}

// Helper function to retrieve CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}


document.querySelectorAll('.cart-form').forEach(form => {
    form.addEventListener('submit', async function (event) {
        event.preventDefault(); // Prevent full-page reload
        const formData = new FormData(this);

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            console.log('Cart updated:', data);

            // Optionally update the UI based on the response
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    });
});


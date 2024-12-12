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

document.querySelectorAll('.cart-action').forEach(button => {
    button.addEventListener('click', async function (event) {
        event.preventDefault(); // Prevent the form submission

        const action = this.getAttribute('data-action'); // "increase" or "decrease"
        const cartId = this.getAttribute('data-cart-id');

        try {
            const response = await fetch('/cart-order/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(), // CSRF token for security
                },
                body: JSON.stringify({
                    action: action,
                    cart_id: cartId,
                }),
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            console.log('Cart updated:', data);

            // Update the quantity in the UI
            const inputField = this.parentElement.querySelector('input[name="quantity"]');
            inputField.value = data.quantity;
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    });
});

document.querySelectorAll('.delete-cart-item').forEach(button => {
    button.addEventListener('click', async function (event) {
        event.preventDefault(); // Prevent default behavior

        const cartId = this.getAttribute('data-cart-id'); // Get cart ID

        try {
            const response = await fetch(`/cart-order/?cart_id=${cartId}`, {
                method: 'DELETE', // Specify DELETE method
                headers: {
                    'X-CSRFToken': getCSRFToken(), // CSRF token for security
                },
            });

            if (response.status === 204) {
                console.log('Item deleted successfully');
                // Optionally remove the item from the UI
                this.closest('.row').remove();
            } else {
                throw new Error(`Failed to delete item. Status code: ${response.status}`);
            }
        } catch (error) {
            console.error('Error deleting cart item:', error);
        }
    });
});


document.querySelectorAll('.cart-action').forEach(button => {
    button.addEventListener('click', async function (event) {
        event.preventDefault(); // Prevent form submission

        const action = this.getAttribute('data-action'); // "increase" or "decrease"
        const cartId = this.getAttribute('data-cart-id');

        try {
            const response = await fetch('/cart-order/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(), // CSRF token for security
                },
                body: JSON.stringify({
                    action: action,
                    cart_id: cartId,
                }),
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            console.log('Cart updated:', data);

            // Update the quantity in the UI
            const inputField = this.parentElement.querySelector('input[name="quantity"]');
            inputField.value = data.quantity;

            // Update the Order Summary dynamically
            document.querySelector('.order-summary').innerHTML = `
                <h5>Order Summary</h5>
                <p>Products Cost: <strong>${data.cart_prices} ₸</strong></p>
                <p>Discount: <strong>- ${data.discount_price} ₸</strong></p>
                <p>Total: <strong>${data.total_price} ₸</strong></p>
                <button class="btn btn-primary w-100 mt-3">Proceed to Checkout</button>
            `;
        } catch (error) {
            console.error('Error updating cart:', error);
        }
    });
});

document.getElementById('checkout-button').addEventListener('click', async function () {
    try {
        const response = await fetch('/cart-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ action: "complete_order" }),
        });

        if (!response.ok) {
            throw new Error(`Failed to complete order: ${response.status}`);
        }

        const data = await response.json();
        console.log(data.message);

        // Clear the cart section
        document.getElementById('cart-section').innerHTML = '<p>Your cart is now empty!</p>';

        // Update the shopping history dynamically
        const historySection = document.getElementById('shopping-history');
        historySection.innerHTML = ''; // Clear any existing history

        data.completed_orders.forEach(order => {
            const orderElement = `
                <div class="list-group-item">
                    <h5>Order #${order.id}</h5>
                    <p>Placed on: ${new Date(order.created_at).toLocaleDateString()}</p>
                    <p>Total: <strong>${order.total_price} ₸</strong></p>
                    <p>Status: <span class="badge bg-success">${order.status}</span></p>
                </div>
            `;
            historySection.innerHTML += orderElement;
        });
    } catch (error) {
        console.error('Error completing order:', error);
        alert("An error occurred while completing your order. Please try again.");
    }
});



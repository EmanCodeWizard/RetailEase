let cart = JSON.parse(localStorage.getItem('cart')) || [];

function addToCart(name, price) {
    const item = { name, price, quantity: 1 };
    const existingItem = cart.find((item) => item.name === name);
    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push(item);
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    window.location.href = 'cart.html'; // Navigate to cart.html after adding to cart
}

function updateCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
}

function renderCart() {
    const cartItems = document.getElementById('cart-items');
    cartItems.innerHTML = '';

    let total = 0;
    let totalQuantity = 0;

    cart.forEach((item, index) => {
        const itemHTML = `
            <div class="cart-item">
                <h3>${item.name}</h3>
                <p>Price: $${item.price.toFixed(2)}</p>
                <div class="quantity-buttons">
                    <button onclick="decreaseQuantity(${index})">-</button>
                    <span class="quantity">${item.quantity}</span>
                    <button onclick="increaseQuantity(${index})">+</button>
                </div>
                <p>Subtotal: $${(item.price * item.quantity).toFixed(2)}</p>
            </div>
        `;
        cartItems.innerHTML += itemHTML;

        total += item.price * item.quantity;
        totalQuantity += item.quantity;
    });

    document.getElementById('total-amount').textContent = total.toFixed(2);
    document.getElementById('total-quantity').textContent = totalQuantity;

    const orderButton = document.getElementById('order-button');
    orderButton.addEventListener('click', () => {
        const queryParams = `totalQuantity=${totalQuantity}&totalAmount=${total.toFixed(2)}`;
        window.location.href = `order.html?${queryParams}`;
    });
}

function increaseQuantity(index) {
    cart[index].quantity++;
    updateCart();
    renderCart(); // Update the cart display after increasing quantity
}

function decreaseQuantity(index) {
    if (cart[index].quantity > 1) {
        cart[index].quantity--;
    } else {
        // Remove item from cart if quantity is 1
        cart.splice(index, 1);
    }
    updateCart();
    renderCart(); // Update the cart display after decreasing quantity
}

// Render initial cart
renderCart();
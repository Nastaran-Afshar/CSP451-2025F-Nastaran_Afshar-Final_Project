const API_BASE = "";

async function fetchJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

async function loadCategories() {
  try {
    const categories = await fetchJSON("/api/v1/categories");
    const select = document.getElementById("categorySelect");
    categories.forEach((cat) => {
      const opt = document.createElement("option");
      opt.value = cat;
      opt.textContent = cat;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Error loading categories", err);
  }
}

async function loadProducts(category = "") {
  try {
    let url = "/api/v1/products";
    if (category) {
      url += `?category=${encodeURIComponent(category)}`;
    }
    const products = await fetchJSON(url);
    const container = document.getElementById("productList");
    container.innerHTML = "";

    products.forEach((p) => {
      const card = document.createElement("div");
      card.className = "product-card";
      card.innerHTML = `
        <h3>${p.name}</h3>
        <p>Category: ${p.category}</p>
        <p>Price: $${p.price.toFixed(2)}</p>
        <button data-id="${p.id}">Add to cart</button>
      `;
      card.querySelector("button").addEventListener("click", () => addToCart(p.id));
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Error loading products", err);
  }
}

async function loadCart() {
  try {
    const cartItems = await fetchJSON("/api/v1/cart");
    const container = document.getElementById("cartItems");
    container.innerHTML = "";

    let total = 0;
    for (const item of cartItems) {
      const line = document.createElement("div");
      line.innerHTML = `
        <span>${item.product_id} x ${item.quantity}</span>
        <button data-id="${item.id}">Remove</button>
      `;
      line.querySelector("button").addEventListener("click", () => removeFromCart(item.id));
      container.appendChild(line);
      // In a real app we'd join with product price; here just show count.
    }
    document.getElementById("cartTotal").textContent =
      `Items in cart: ${cartItems.length}`;
  } catch (err) {
    console.error("Error loading cart", err);
  }
}

async function addToCart(productId) {
  try {
    await fetch("/api/v1/cart/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    await loadCart();
  } catch (err) {
    console.error("Error adding to cart", err);
  }
}

async function removeFromCart(id) {
  try {
    await fetch(`/api/v1/cart/items/${id}`, {
      method: "DELETE",
    });
    await loadCart();
  } catch (err) {
    console.error("Error removing from cart", err);
  }
}

async function checkout() {
  const status = document.getElementById("orderStatus");
  status.textContent = "Placing order...";
  try {
    const res = await fetch("/api/v1/orders", { method: "POST" });
    if (!res.ok) {
      const body = await res.json();
      status.textContent = `Error: ${body.detail || "Unable to place order"}`;
      return;
    }
    const order = await res.json();
    status.textContent = `Order ${order.id} confirmed!`;
    await loadCart();
  } catch (err) {
    console.error("Error placing order", err);
    status.textContent = "Error placing order.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadCategories();
  loadProducts();
  loadCart();

  document.getElementById("categorySelect").addEventListener("change", (e) => {
    loadProducts(e.target.value);
  });

  document.getElementById("checkoutBtn").addEventListener("click", checkout);
});

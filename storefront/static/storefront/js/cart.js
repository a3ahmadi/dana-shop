(() => {
    "use strict";

    const page = document.getElementById("cartPage");
    if (!page) return;

    const items = document.getElementById("cartItems");
    const status = document.getElementById("cartStatus");
    const csrfToken = page.querySelector('[name="csrfmiddlewaretoken"]').value;
    const format = value => new Intl.NumberFormat("fa-IR").format(value);

    function refreshTotals() {
        const rows = [...items.querySelectorAll(".cart-item")];
        let count = 0;
        let original = 0;
        let total = 0;
        rows.forEach(row => {
            const quantity = Number(row.dataset.quantity);
            const price = Number(row.dataset.price);
            const finalPrice = Number(row.dataset.finalPrice);
            count += quantity;
            original += price * quantity;
            total += finalPrice * quantity;
            row.querySelector(".cart-quantity").textContent = format(quantity);
            row.querySelector(".cart-line-total").textContent = format(finalPrice * quantity);
        });
        document.getElementById("cartItemCount").textContent = `${format(count)} کالا`;
        document.getElementById("cartOriginalPrice").textContent = format(original);
        document.getElementById("cartDiscount").textContent = format(original - total);
        document.getElementById("cartTotal").textContent = format(total);
        const checkoutLink = document.getElementById("checkoutLink");
        if (!rows.length) {
            checkoutLink.removeAttribute("href");
            checkoutLink.setAttribute("aria-disabled", "true");
            checkoutLink.setAttribute("tabindex", "-1");
            checkoutLink.classList.add("opacity-60", "pointer-events-none");
        }
        if (!rows.length && !document.getElementById("cartEmpty")) {
            const empty = document.createElement("div");
            empty.id = "cartEmpty";
            empty.className = "text-center py-10 text-gray-600 dark:text-gray-300";
            empty.textContent = "سبد خرید شما خالی است. ";
            const link = document.createElement("a");
            link.href = "/products/";
            link.className = "text-primary-600 font-bold";
            link.textContent = "مشاهده محصولات";
            empty.append(link);
            items.append(empty);
        }
        window.dispatchEvent(new Event("cart:changed"));
    }

    items.addEventListener("click", async event => {
        const button = event.target.closest("[data-cart-action]");
        if (!button || button.disabled) return;
        const row = button.closest(".cart-item");
        const action = button.dataset.cartAction;
        const quantity = Number(row.dataset.quantity);
        const nextQuantity = quantity + (action === "increase" ? 1 : -1);
        if (action !== "delete" && (nextQuantity < 1 || nextQuantity > Number(row.dataset.stock))) return;
        const productId = row.dataset.productId;
        const colorId = row.dataset.colorId;
        const url = action === "delete"
            ? `/api/v1/cart/items/${productId}/delete/?color_id=${colorId}`
            : `/api/v1/cart/items/${productId}/`;
        row.querySelectorAll("button").forEach(control => { control.disabled = true; });
        status.textContent = "";
        try {
            const response = await fetch(url, {
                method: action === "delete" ? "DELETE" : "PATCH",
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                ...(action === "delete" ? {} : {body: JSON.stringify({color_id: Number(colorId), quantity: nextQuantity})}),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                const detail = data.detail || data.quantity?.[0] || data.color_id?.[0];
                throw new Error(typeof detail === "string" ? detail : "تغییر سبد خرید انجام نشد. دوباره تلاش کنید.");
            }
            if (action === "delete") row.remove();
            else row.dataset.quantity = String(nextQuantity);
            refreshTotals();
        } catch (error) {
            status.textContent = error.message || "ارتباط با فروشگاه برقرار نشد. دوباره تلاش کنید.";
        } finally {
            row.querySelectorAll("button").forEach(control => { control.disabled = false; });
            if (row.isConnected) {
                row.querySelector('[data-cart-action="decrease"]').disabled = Number(row.dataset.quantity) <= 1;
                row.querySelector('[data-cart-action="increase"]').disabled = Number(row.dataset.quantity) >= Number(row.dataset.stock);
            }
        }
    });
})();

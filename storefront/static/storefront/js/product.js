(() => {
    "use strict";

    document.addEventListener("DOMContentLoaded", () => {
        const detail = document.getElementById("productDetail");
        if (!detail) return;
        const mainImage = document.getElementById("productMainImage");
        const thumbnails = [...document.querySelectorAll("[data-gallery-image]")];
        thumbnails.forEach(button => button.addEventListener("click", () => {
            if (!mainImage) return;
            mainImage.src = button.dataset.galleryImage;
            thumbnails.forEach(item => {
                const selected = item === button;
                item.setAttribute("aria-pressed", String(selected));
                item.classList.toggle("border-primary", selected);
                item.classList.toggle("border-gray-300", !selected);
            });
        }));

        const form = document.getElementById("addToCartForm");
        const input = document.getElementById("productQuantity");
        const submit = document.getElementById("addToCartButton");
        const status = document.getElementById("addToCartStatus");
        const stock = Number(detail.dataset.stock) || 0;
        const quantity = () => {
            const value = Number.parseInt(input.value, 10);
            const clamped = Math.min(stock, Math.max(1, Number.isFinite(value) ? value : 1));
            input.value = String(clamped);
            return clamped;
        };

        document.getElementById("increaseQuantity")?.addEventListener("click", () => {
            input.value = String(quantity() + 1);
            quantity();
        });
        document.getElementById("decreaseQuantity")?.addEventListener("click", () => {
            input.value = String(quantity() - 1);
            quantity();
        });
        input?.addEventListener("change", quantity);

        form?.addEventListener("submit", async event => {
            event.preventDefault();
            const color = document.querySelector('input[name="product-color"]:checked');
            if (!color || stock < 1) return;
            submit.disabled = true;
            status.textContent = "در حال افزودن به سبد خرید…";
            status.className = "text-sm text-gray-600 dark:text-gray-300";
            try {
                const response = await fetch("/api/v1/cart/items/", {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": form.querySelector('[name="csrfmiddlewaretoken"]').value,
                    },
                    body: JSON.stringify({
                        product_id: Number(detail.dataset.productId),
                        color_id: Number(color.value),
                        quantity: quantity(),
                    }),
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(typeof result.detail === "string"
                        ? result.detail
                        : "افزودن محصول به سبد خرید انجام نشد. لطفاً دوباره تلاش کنید.");
                }
                window.dispatchEvent(new Event("cart:changed"));
                status.textContent = result.message || "محصول به سبد خرید اضافه شد.";
                status.className = "text-sm text-green-700 dark:text-green-400";
            } catch (error) {
                status.textContent = error.message || "خطا در ارتباط با فروشگاه. لطفاً دوباره تلاش کنید.";
                status.className = "text-sm text-red-600 dark:text-red-400";
            } finally {
                submit.disabled = false;
            }
        });
    });
})();
(() => {
    "use strict";

    const form = document.getElementById("confirmOrderForm");
    if (!form) return;

    const button = document.getElementById("confirmOrderButton");
    const status = document.getElementById("confirmOrderStatus");
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;

    function errorText(data) {
        if (typeof data.detail === "string") return data.detail;
        for (const value of Object.values(data)) {
            if (typeof value === "string") return value;
            if (Array.isArray(value) && typeof value[0] === "string") return value[0];
        }
        return "درخواست انجام نشد. دوباره تلاش کنید.";
    }

    async function post(url, payload) {
        const response = await fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {"Accept": "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken},
            body: JSON.stringify(payload),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorText(data));
        return data;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        if (button.disabled) return;
        button.disabled = true;
        status.textContent = "در حال آماده‌سازی پرداخت…";
        let orderCreated = false;
        try {
            const orderResponse = await post("/api/v1/orders/create/", {
                address_id: Number(form.dataset.addressId),
                shipping_method: form.dataset.shippingMethod,
            });
            orderCreated = true;
            const paymentResponse = await post("/api/v1/payments/create/", {order_id: orderResponse.order.id});
            const paymentUrl = new URL(paymentResponse.payment.payment_url);
            if (paymentUrl.protocol !== "https:") throw new Error("نشانی درگاه پرداخت معتبر نیست.");
            window.location.assign(paymentUrl.href);
        } catch (error) {
            status.textContent = orderCreated
                ? `سفارش در انتظار پرداخت ثبت شد، اما اتصال به درگاه انجام نشد: ${error.message}`
                : error.message;
            button.disabled = false;
        }
    });
})();

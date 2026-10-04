(() => {
    "use strict";

    const page = document.getElementById("checkoutPage");
    if (!page) return;

    const form = document.getElementById("checkoutForm");
    const addressList = document.getElementById("savedAddresses");
    const modal = document.getElementById("addressModal");
    const addressForm = document.getElementById("addressForm");
    const checkoutStatus = document.getElementById("checkoutStatus");
    const addressStatus = document.getElementById("addressStatus");
    const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]').value;
    const firstName = document.getElementById("checkoutFirstName");
    const lastName = document.getElementById("checkoutLastName");
    let savedName = [firstName.value.trim(), lastName.value.trim()];

    function errorText(data, fallback) {
        if (typeof data.detail === "string") return data.detail;
        for (const value of Object.values(data)) {
            if (typeof value === "string") return value;
            if (Array.isArray(value) && typeof value[0] === "string") return value[0];
        }
        return fallback;
    }

    async function apiRequest(url, method, body) {
        const response = await fetch(url, {
            method,
            credentials: "same-origin",
            headers: {"Accept": "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken},
            ...(body === undefined ? {} : {body: JSON.stringify(body)}),
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(errorText(data, "درخواست انجام نشد. دوباره تلاش کنید."));
        return data;
    }

    function selectedAddress() {
        return addressList.querySelector('input[name="address_id"]:checked');
    }

    function updateShipping() {
        const chosen = selectedAddress();
        const city = chosen?.closest("[data-city]").dataset.city.trim().replaceAll("ي", "ی").replace(/\s+/g, " ");
        const tehran = city === "تهران";
        const courier = document.getElementById("courierOption");
        const tipax = document.getElementById("tipaxOption");
        courier.hidden = !chosen || !tehran;
        tipax.hidden = !chosen;
        courier.classList.toggle("hidden", !chosen || !tehran);
        tipax.classList.toggle("hidden", !chosen);
        const previous = form.querySelector('input[name="shipping_method"]:checked')?.value;
        const method = chosen ? (previous === "tipax" || !tehran ? "tipax" : "courier") : "";
        courier.querySelector("input").checked = method === "courier";
        tipax.querySelector("input").checked = method === "tipax";
        document.getElementById("shippingHint").hidden = Boolean(chosen);
        updateShippingSummary();
        addressList.querySelectorAll(".address-item").forEach(label => {
            const active = label.querySelector("input").checked;
            label.classList.toggle("border-primary-500", active);
            label.classList.toggle("bg-blue-50", active);
            label.classList.toggle("dark:bg-zinc-800", active);
        });
    }

    function updateShippingSummary() {
        const method = form.querySelector('input[name="shipping_method"]:checked')?.value;
        document.getElementById("selectedShipping").textContent = method === "courier" ? "پیک موتوری" : method === "tipax" ? "تیپاکس" : "پس از انتخاب آدرس";
    }

    function addressNode(address, selected) {
        const label = document.createElement("label");
        label.className = "address-item block border border-gray-300 dark:border-gray-600 rounded-lg p-4 cursor-pointer hover:border-primary-500 transition-all";
        label.dataset.city = address.city;
        const row = document.createElement("span");
        row.className = "flex items-start gap-3";
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "address_id";
        radio.value = String(address.id);
        radio.className = "mt-1";
        radio.required = true;
        radio.checked = address.id === selected;
        const text = document.createElement("span");
        text.className = "flex-1";
        const title = document.createElement("strong");
        title.className = "block text-gray-800 dark:text-white";
        title.textContent = address.title + (address.is_default ? " (پیش‌فرض)" : "");
        const recipient = document.createElement("span");
        recipient.className = "block text-sm text-gray-600 dark:text-gray-300 mt-1";
        recipient.textContent = `${address.recipient_name} | ${address.phone}`;
        const location = document.createElement("span");
        location.className = "block text-sm text-gray-600 dark:text-gray-300 mt-1";
        location.textContent = `${address.state}، ${address.city}، ${address.complete_address}`;
        const postal = document.createElement("span");
        postal.className = "block text-xs text-gray-500 mt-1";
        postal.textContent = `کد پستی: ${address.postal_code}`;
        text.append(title, recipient, location, postal);
        row.append(radio, text);
        label.append(row);
        return label;
    }

    function renderAddresses(addresses, selectedId) {
        addressList.replaceChildren(...addresses.map(address => addressNode(address, selectedId)));
        const addButton = document.getElementById("openAddressModal");
        addButton.disabled = addresses.length >= 3;
        addButton.title = addButton.disabled ? "حداکثر سه آدرس می‌توانید ثبت کنید." : "";
        updateShipping();
    }

    addressList.addEventListener("change", updateShipping);
    form.querySelectorAll('input[name="shipping_method"]').forEach(input => input.addEventListener("change", updateShippingSummary));
    updateShipping();

    document.getElementById("openAddressModal").addEventListener("click", () => {
        addressStatus.textContent = "";
        addressForm.reset();
        addressForm.elements.recipient_name.value = `${firstName.value.trim()} ${lastName.value.trim()}`.trim();
        addressForm.elements.phone.value = document.querySelector("#checkoutPage [dir=ltr]")?.textContent.trim() || "";
        addressForm.elements.is_default.checked = !selectedAddress();
        modal.showModal();
    });
    document.getElementById("closeAddressModal").addEventListener("click", () => modal.close());
    modal.addEventListener("click", event => { if (event.target === modal) modal.close(); });

    addressForm.addEventListener("submit", async event => {
        event.preventDefault();
        if (!addressForm.reportValidity()) return;
        const button = document.getElementById("saveAddress");
        button.disabled = true;
        addressStatus.textContent = "";
        const payload = Object.fromEntries(new FormData(addressForm));
        payload.is_default = addressForm.elements.is_default.checked;
        try {
            const created = await apiRequest("/api/v1/addresses/", "POST", payload);
            const result = await apiRequest("/api/v1/addresses/", "GET");
            renderAddresses(Array.isArray(result) ? result : (result.results || []), created.id);
            modal.close();
        } catch (error) {
            addressStatus.textContent = error.message;
        } finally {
            button.disabled = false;
        }
    });

    form.addEventListener("submit", async event => {
        event.preventDefault();
        checkoutStatus.textContent = "";
        const chosen = selectedAddress();
        if (!chosen) {
            checkoutStatus.textContent = "یک آدرس انتخاب یا اضافه کنید.";
            document.getElementById("openAddressModal").focus();
            return;
        }
        if (!form.reportValidity()) return;
        const name = [firstName.value.trim(), lastName.value.trim()];
        if (!name[0] || !name[1]) {
            checkoutStatus.textContent = "نام و نام خانوادگی را کامل کنید.";
            return;
        }
        const button = document.getElementById("saveCheckout");
        button.disabled = true;
        try {
            if (name[0] !== savedName[0] || name[1] !== savedName[1]) {
                await apiRequest("/api/v1/accounts/profile/", "PATCH", {first_name: name[0], last_name: name[1]});
                savedName = name;
            }
            const method = form.querySelector('input[name="shipping_method"]:checked')?.value;
            await apiRequest("/api/v1/checkout/", "POST", {
                address_id: Number(chosen.value),
                shipping_method: method,
                payment_method: "online",
            });
            window.location.assign("/accept/");
        } catch (error) {
            checkoutStatus.textContent = error.message;
            checkoutStatus.className = "text-sm mt-3 text-red-600 dark:text-red-400";
        } finally {
            button.disabled = false;
        }
    });
})();

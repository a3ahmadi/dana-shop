(() => {
    "use strict";

    const root = document.getElementById("userPanel");
    if (!root) return;

    const profilePanel = document.getElementById("panelProfile");
    const ordersPanel = document.getElementById("panelOrders");
    const listPane = document.getElementById("panelOrdersList");
    const detailPane = document.getElementById("panelOrderDetail");
    const tabs = Array.from(root.querySelectorAll("[data-panel-tab]"));
    const statusFilter = document.getElementById("panelOrderStatus");
    const periodFilter = document.getElementById("panelOrderPeriod");
    const searchInput = document.getElementById("panelOrderSearch");
    const orderCards = Array.from(root.querySelectorAll(".panel-order-card"));
    const visibleCount = document.getElementById("panelVisibleCount");
    const activeCount = document.getElementById("panelActiveCount");
    const noMatches = document.getElementById("panelNoMatches");
    const ordersStatus = document.getElementById("panelOrdersStatus");
    const csrfToken = root.querySelector('[name="csrfmiddlewaretoken"]').value;
    let detailRequest;

    function showTab(tab) {
        const orders = tab === "orders";
        profilePanel.hidden = orders;
        ordersPanel.hidden = !orders;
        tabs.forEach(link => {
            const active = link.dataset.panelTab === tab;
            link.setAttribute("aria-current", active ? "page" : "false");
            link.classList.toggle("bg-blue-50", active);
            link.classList.toggle("text-primary", active);
            link.classList.toggle("text-gray-700", !active);
        });
    }

    function showList(push = true) {
        detailRequest?.abort();
        listPane.hidden = false;
        detailPane.hidden = true;
        showTab("orders");
        if (push) history.pushState({}, "", "/panel/?tab=orders");
    }

    async function showDetail(id, push = true) {
        detailRequest?.abort();
        detailRequest = new AbortController();
        showTab("orders");
        detailPane.hidden = false;
        listPane.hidden = true;
        detailPane.textContent = "در حال دریافت جزئیات سفارش…";
        try {
            const response = await fetch(`/panel/orders/${id}/?fragment=1`, {
                credentials: "same-origin",
                signal: detailRequest.signal,
                headers: {"X-Requested-With": "XMLHttpRequest"},
            });
            if (response.redirected) {
                window.location.assign("/");
                return;
            }
            if (!response.ok) throw new Error("جزئیات این سفارش در دسترس نیست.");
            detailPane.innerHTML = await response.text();
            if (push) history.pushState({}, "", `/panel/orders/${id}/`);
        } catch (error) {
            if (error.name === "AbortError") return;
            detailPane.textContent = error.message;
        }
    }

    function normalize(value) {
        return String(value).toLocaleLowerCase("fa").replace(/[۰-۹٠-٩]/g, digit =>
            String("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩".indexOf(digit) % 10));
    }

    function applyFilters() {
        const status = statusFilter.value;
        const days = Number(periodFilter.value);
        const query = normalize(searchInput.value.trim());
        const now = Date.now();
        let visible = 0;
        let active = 0;
        orderCards.forEach(card => {
            const orderStatus = card.dataset.status;
            if (["pending", "paid", "processing", "shipping"].includes(orderStatus)) active++;
            const created = Number(card.dataset.created) * 1000;
            const matches = (!status || orderStatus === status)
                && (!days || (now - created) <= days * 86400000)
                && (!query || normalize(card.dataset.search).includes(query));
            card.hidden = !matches;
            if (matches) visible++;
        });
        activeCount.textContent = String(active);
        visibleCount.textContent = `${visible} سفارش`;
        if (noMatches) noMatches.hidden = visible !== 0;
    }

    function errorText(data) {
        if (typeof data.detail === "string") return data.detail;
        for (const value of Object.values(data)) {
            if (typeof value === "string") return value;
            if (Array.isArray(value) && typeof value[0] === "string") return value[0];
        }
        return "درخواست انجام نشد. دوباره تلاش کنید.";
    }

    tabs.forEach(link => link.addEventListener("click", event => {
        event.preventDefault();
        if (link.dataset.panelTab === "orders") showList();
        else {
            detailRequest?.abort();
            showTab("profile");
            history.pushState({}, "", "/panel/");
        }
    }));

    root.addEventListener("click", async event => {
        const detailLink = event.target.closest("[data-order-detail]");
        if (detailLink) {
            event.preventDefault();
            await showDetail(detailLink.dataset.orderDetail);
            return;
        }
        const backLink = event.target.closest("[data-back-orders]");
        if (backLink) {
            event.preventDefault();
            showList();
            return;
        }
        const cancelButton = event.target.closest("[data-cancel-order]");
        if (!cancelButton) return;
        const warning = cancelButton.dataset.paid === "1"
            ? "این سفارش پرداخت شده است. بازگشت وجه به‌صورت خودکار انجام نمی‌شود. لغو شود؟"
            : "این سفارش لغو شود؟";
        if (!window.confirm(warning)) return;
        cancelButton.disabled = true;
        try {
            const response = await fetch(`/api/v1/orders/${cancelButton.dataset.cancelOrder}/cancel/`, {
                method: "POST",
                credentials: "same-origin",
                headers: {"Accept": "application/json", "X-CSRFToken": csrfToken},
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(errorText(data));
            const card = cancelButton.closest(".panel-order-card");
            card.dataset.status = "cancelled";
            const badge = card.querySelector(".panel-order-status");
            badge.textContent = "لغو شده";
            badge.className = "panel-order-status inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800";
            cancelButton.remove();
            ordersStatus.textContent = cancelButton.dataset.paid === "1"
                ? "سفارش لغو شد. بازگشت وجه به‌صورت خودکار انجام نمی‌شود."
                : "سفارش لغو شد.";
            ordersStatus.className = "text-sm mt-4 text-green-700 dark:text-green-400";
            applyFilters();
        } catch (error) {
            ordersStatus.textContent = error.message;
            ordersStatus.className = "text-sm mt-4 text-red-600 dark:text-red-400";
            cancelButton.disabled = false;
        }
    });

    [statusFilter, periodFilter].forEach(select => select.addEventListener("change", applyFilters));
    searchInput.addEventListener("input", applyFilters);
    applyFilters();

    const profileForm = document.getElementById("panelProfileForm");
    const saveButton = document.getElementById("panelSaveProfile");
    const profileStatus = document.getElementById("panelProfileStatus");
    profileForm.addEventListener("submit", async event => {
        event.preventDefault();
        saveButton.disabled = true;
        const data = Object.fromEntries(new FormData(profileForm));
        delete data.csrfmiddlewaretoken;
        try {
            const response = await fetch("/api/v1/accounts/profile/", {
                method: "PATCH",
                credentials: "same-origin",
                headers: {"Accept": "application/json", "Content-Type": "application/json", "X-CSRFToken": csrfToken},
                body: JSON.stringify(data),
            });
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(errorText(result));
            document.getElementById("panelProfileName").textContent =
                `${result.first_name} ${result.last_name}`.trim() || "حساب کاربری من";
            profileStatus.textContent = "اطلاعات حساب ذخیره شد.";
            profileStatus.className = "text-sm text-green-700 dark:text-green-400";
        } catch (error) {
            profileStatus.textContent = error.message;
            profileStatus.className = "text-sm text-red-600 dark:text-red-400";
        } finally {
            saveButton.disabled = false;
        }
    });

    window.addEventListener("popstate", () => {
        const detailMatch = window.location.pathname.match(/^\/panel\/orders\/(\d+)\/$/);
        if (detailMatch) showDetail(detailMatch[1], false);
        else if (new URLSearchParams(window.location.search).get("tab") === "orders") showList(false);
        else showTab("profile");
    });
})();

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("catalogSearchForm");
    const input = document.getElementById("catalogSearchInput");
    const results = document.getElementById("catalogSearchResults");
    if (!form || !input || !results) return;

    let timer;
    let controller;
    let requestId = 0;
    const allResultsUrl = query => "/products/?search=" + encodeURIComponent(query);

    function hideResults() {
        results.classList.add("hidden");
        input.setAttribute("aria-expanded", "false");
    }

    function showResults() {
        results.classList.remove("hidden");
        input.setAttribute("aria-expanded", "true");
    }

    async function search(query) {
        controller?.abort();
        const currentRequest = ++requestId;
        if (!query) {
            results.replaceChildren();
            hideResults();
            return;
        }
        controller = new AbortController();
        results.textContent = "در حال جستجو…";
        showResults();
        try {
            const response = await fetch("/api/v1/products/?search=" + encodeURIComponent(query), {
                signal: controller.signal,
                credentials: "same-origin",
                headers: { Accept: "application/json" },
            });
            if (!response.ok) throw new Error("Search request failed: " + response.status);
            const data = await response.json();
            const products = Array.isArray(data) ? data : data.results;
            if (!Array.isArray(products)) throw new Error("Unexpected search response");
            if (currentRequest !== requestId || query !== input.value.trim()) return;

            results.replaceChildren();
            if (!products.length) {
                results.textContent = "محصولی پیدا نشد.";
                return;
            }
            products.slice(0, 6).forEach(product => {
                const link = document.createElement("a");
                link.href = "/products/" + encodeURIComponent(product.slug) + "/";
                link.className = "block p-3 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-zinc-800";
                const name = document.createElement("strong");
                name.className = "block text-sm";
                name.textContent = product.name;
                const category = document.createElement("span");
                category.className = "block text-xs text-gray-500 mt-1";
                category.textContent = product.category || "";
                link.append(name, category);
                results.append(link);
            });
            const viewAll = document.createElement("a");
            viewAll.href = allResultsUrl(query);
            viewAll.className = "block p-3 text-sm font-bold text-primary hover:bg-gray-100 dark:hover:bg-zinc-800";
            viewAll.textContent = "نمایش همه نتایج";
            results.append(viewAll);
        } catch (error) {
            if (error.name === "AbortError" || currentRequest !== requestId) return;
            results.textContent = "جستجو انجام نشد. دوباره تلاش کنید.";
            showResults();
        }
    }

    input.addEventListener("input", () => {
        clearTimeout(timer);
        const query = input.value.trim();
        if (!query) {
            controller?.abort();
            requestId++;
            results.replaceChildren();
            hideResults();
        } else {
            timer = setTimeout(() => search(query), 250);
        }
    });
    input.addEventListener("focus", () => {
        if (input.value.trim()) search(input.value.trim());
    });
    form.addEventListener("submit", event => {
        event.preventDefault();
        clearTimeout(timer);
        const query = input.value.trim();
        if (!query) {
            input.focus();
            return;
        }
        search(query);
    });
    document.getElementById("mobileSearchButton")?.addEventListener("click", event => {
        event.preventDefault();
        input.focus();
        input.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    document.addEventListener("click", event => {
        if (!form.contains(event.target)) hideResults();
    });
});
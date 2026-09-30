(() => {
    "use strict";

    const API_BASE = "/api/v1";
    const PAGE_SIZE = 12;
    const SEARCH_DEBOUNCE_MS = 350;

    const state = {
        search: "",
        category: "",
        categoryName: "",
        color: "",
        colorName: "",
        minPrice: "",
        maxPrice: "",
        inStock: false,
        ordering: "",
        page: 1,
        total: 0,
        categories: [],
        colors: [],
        productRequestController: null,
        searchTimer: null,
        clientSideProducts: null,
    };

    const elements = {};

    document.addEventListener("DOMContentLoaded", initProductsPage);

    async function initProductsPage() {
        cacheElements();
        restoreStateFromUrl();
        bindEvents();
        syncControlsFromState();
        setActiveSortButton();

        await Promise.allSettled([
            loadCategories(),
            loadColors(),
        ]);

        await loadProducts();
    }

    function cacheElements() {
        elements.categoriesLoading = document.getElementById("categoriesLoading");
        elements.categoriesCarousel = document.getElementById("categoriesCarousel");
        elements.categoriesContainer = document.getElementById("categoriesContainer");
        elements.productsLoading = document.getElementById("productsLoading");
        elements.productsGrid = document.getElementById("productsGrid");
        elements.productsError = document.getElementById("productsError");
        elements.productsEmpty = document.getElementById("productsEmpty");
        elements.productsPagination = document.getElementById("productsPagination");
        elements.productsResultCount = document.getElementById("productsResultCount");
        elements.retryProductsButton = document.getElementById("retryProductsButton");
        elements.sortButtons = [...document.querySelectorAll("[data-ordering]")];
        elements.filterPanels = [...document.querySelectorAll("[data-filter-panel]")];
        elements.clearButtons = [...document.querySelectorAll("[data-clear-filters]")];
        elements.colorSections = [...document.querySelectorAll("[data-color-filter-section]")];
    }

    function bindEvents() {
        elements.retryProductsButton?.addEventListener("click", loadProducts);

        elements.sortButtons.forEach(button => {
            button.addEventListener("click", () => {
                state.ordering = button.dataset.ordering || "";
                state.page = 1;
                setActiveSortButton();
                updateUrl();
                loadProducts();
            });
        });

        elements.clearButtons.forEach(button => {
            button.addEventListener("click", clearAllFilters);
        });

        elements.filterPanels.forEach(panel => {
            const searchInput = panel.querySelector("[data-filter-search]");
            const minInput = panel.querySelector("[data-min-price]");
            const maxInput = panel.querySelector("[data-max-price]");
            const applyPriceButton = panel.querySelector("[data-apply-price]");
            const inStockInput = panel.querySelector("[data-in-stock]");

            searchInput?.addEventListener("input", event => {
                state.search = event.target.value.trim();
                state.page = 1;
                syncSearchInputs(event.target);
                clearTimeout(state.searchTimer);
                state.searchTimer = setTimeout(() => {
                    updateUrl();
                    loadProducts();
                }, SEARCH_DEBOUNCE_MS);
            });

            applyPriceButton?.addEventListener("click", () => {
                state.minPrice = normalizePriceValue(minInput?.value);
                state.maxPrice = normalizePriceValue(maxInput?.value);

                if (state.minPrice && state.maxPrice && Number(state.minPrice) > Number(state.maxPrice)) {
                    [state.minPrice, state.maxPrice] = [state.maxPrice, state.minPrice];
                }

                state.page = 1;
                syncPriceInputs();
                renderActiveFilters();
                updateUrl();
                loadProducts();
            });

            inStockInput?.addEventListener("change", event => {
                state.inStock = event.target.checked;
                state.page = 1;
                syncInStockInputs(event.target);
                renderActiveFilters();
                updateUrl();
                loadProducts();
            });
        });
    }

    async function loadCategories() {
        try {
            const response = await fetchJson(`${API_BASE}/categories/?limit=100`);
            state.categories = normalizeListResponse(response);
            if (state.category) {
                const selectedCategory = state.categories.find(category => String(category.id) === String(state.category));
                state.categoryName = selectedCategory?.name || "";
            }
            renderCategories();
        } catch (error) {
            console.error("Could not load categories", error);
            elements.categoriesLoading?.remove();
            document.getElementById("categoriesSection")?.classList.add("hidden");
        }
    }

    async function loadColors() {
        try {
            const response = await fetchJson(`${API_BASE}/colors/?limit=100`);
            state.colors = normalizeListResponse(response);
            if (state.color) {
                const selectedColor = state.colors.find(color => String(color.id) === String(state.color));
                state.colorName = selectedColor?.name || "";
            }
            renderColorOptions();
            renderActiveFilters();
        } catch (error) {
            // The current backend does not expose colors until the included backend patch is applied.
            console.warn("Color API is unavailable. Color filter has been hidden.", error);
            elements.colorSections.forEach(section => section.classList.add("hidden"));
        }
    }

    async function loadProducts() {
        showProductsLoading();

        if (state.productRequestController) {
            state.productRequestController.abort();
        }

        const controller = new AbortController();
        state.productRequestController = controller;

        try {
            const query = buildProductQuery();
            const response = await fetchJson(`${API_BASE}/products/?${query.toString()}`, {
                signal: controller.signal,
            });

            if (Array.isArray(response)) {
                // Backward compatible with the current unpaginated API.
                state.clientSideProducts = response;
                state.total = response.length;
                const offset = (state.page - 1) * PAGE_SIZE;
                renderProducts(response.slice(offset, offset + PAGE_SIZE));
            } else {
                state.clientSideProducts = null;
                const results = Array.isArray(response?.results) ? response.results : [];
                state.total = Number(response?.count ?? results.length);
                renderProducts(results);
            }

            renderPagination();
            renderResultCount();
            renderActiveFilters();
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Could not load products", error);
            showProductsError();
        } finally {
            if (state.productRequestController === controller) {
                state.productRequestController = null;
            }
        }
    }

    function buildProductQuery() {
        const params = new URLSearchParams();

        if (state.search) params.set("search", state.search);
        if (state.category) params.set("category", state.category);
        if (state.color) params.set("color", state.color);
        if (state.minPrice) params.set("min_price", state.minPrice);
        if (state.maxPrice) params.set("max_price", state.maxPrice);
        if (state.inStock) params.set("in_stock", "true");
        if (state.ordering) params.set("ordering", state.ordering);

        // Works after applying the backend pagination patch. Ignored safely by the old API.
        params.set("limit", String(PAGE_SIZE));
        params.set("offset", String((state.page - 1) * PAGE_SIZE));

        return params;
    }

    function renderCategories() {
        if (!elements.categoriesContainer) return;

        const allCard = categoryCardTemplate({
            id: "",
            name: "همه محصولات",
            image: "",
            product_count: null,
        });

        const categoryCards = state.categories.map(category => categoryCardTemplate(category)).join("");
        elements.categoriesContainer.innerHTML = allCard + categoryCards;

        elements.categoriesContainer.querySelectorAll("[data-category-id]").forEach(button => {
            button.addEventListener("click", event => {
                event.preventDefault();
                const categoryId = button.dataset.categoryId || "";
                const categoryName = button.dataset.categoryName || "";

                state.category = categoryId;
                state.categoryName = categoryName;
                state.page = 1;
                updateSelectedCategoryCards();
                renderActiveFilters();
                updateUrl();
                loadProducts();
            });
        });

        elements.categoriesLoading?.classList.add("hidden");
        elements.categoriesCarousel?.classList.remove("hidden");
        updateSelectedCategoryCards();

        requestAnimationFrame(() => {
            const sliderElement = elements.categoriesCarousel;
            if (!sliderElement || typeof window.Swiper === "undefined") return;

            if (sliderElement.swiper) {
                sliderElement.swiper.update();
                return;
            }

            new window.Swiper(sliderElement, {
                slidesPerView: "auto",
                spaceBetween: 12,
                freeMode: true,
            });
        });
    }

    function categoryCardTemplate(category) {
        const selected = String(category.id ?? "") === String(state.category);
        const image = resolveMediaUrl(category.image);
        const countText = category.product_count !== null && category.product_count !== undefined && Number.isFinite(Number(category.product_count))
            ? `<span class="text-[11px] text-gray-400">${toPersianDigits(formatNumber(category.product_count))} محصول</span>`
            : "";

        return `
            <div class="swiper-slide !w-40 !h-40">
                <button type="button"
                        data-category-id="${escapeHtml(category.id ?? "")}"
                        data-category-name="${escapeHtml(category.name ?? "")}"
                        class="category-card w-full h-full bg-white dark:bg-custom-dark dark:border-gray-700 dark:text-gray-200 space-y-2 shadow-sm border ${selected ? "border-primary ring-1 ring-primary" : "border-gray-200"} p-3 rounded-2xl flex flex-col items-center justify-center duration-200 hover:shadow-md hover:scale-[1.02] transition-all">
                    <figure class="w-20 h-20 flex items-center justify-center overflow-hidden rounded-xl bg-gray-50 dark:bg-gray-800">
                        ${image
                            ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(category.name || "دسته‌بندی")}" class="w-full h-full object-contain" loading="lazy">`
                            : categoryFallbackIcon()
                        }
                    </figure>
                    <h3 class="text-sm font-medium text-gray-900 dark:text-gray-200 text-center line-clamp-1">${escapeHtml(category.name || "همه محصولات")}</h3>
                    ${countText}
                </button>
            </div>
        `;
    }

    function updateSelectedCategoryCards() {
        document.querySelectorAll("[data-category-id]").forEach(card => {
            const isSelected = String(card.dataset.categoryId || "") === String(state.category || "");
            card.classList.toggle("border-primary", isSelected);
            card.classList.toggle("ring-1", isSelected);
            card.classList.toggle("ring-primary", isSelected);
            card.classList.toggle("border-gray-200", !isSelected);
        });
    }

    function renderColorOptions() {
        if (!state.colors.length) {
            elements.colorSections.forEach(section => section.classList.add("hidden"));
            return;
        }

        elements.filterPanels.forEach(panel => {
            const container = panel.querySelector("[data-color-options]");
            if (!container) return;

            const panelKey = panel.dataset.filterPanel || "panel";
            container.innerHTML = `
                <label class="cursor-pointer">
                    <input type="radio" name="color-${panelKey}" value="" class="sr-only" ${!state.color ? "checked" : ""}>
                    <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-300 dark:border-gray-600 text-xs hover:border-primary">همه</span>
                </label>
            ` + state.colors.map(color => `
                <label class="cursor-pointer">
                    <input type="radio" name="color-${panelKey}" value="${escapeHtml(color.id)}" class="sr-only" ${String(state.color) === String(color.id) ? "checked" : ""}>
                    <span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-300 dark:border-gray-600 text-xs hover:border-primary">
                        <span class="size-3.5 rounded-full border border-gray-300" style="background:${safeColor(color.hex_code)}"></span>
                        ${escapeHtml(color.name)}
                    </span>
                </label>
            `).join("");

            container.querySelectorAll('input[type="radio"]').forEach(input => {
                input.addEventListener("change", () => {
                    if (!input.checked) return;
                    state.color = input.value;
                    const selected = state.colors.find(color => String(color.id) === String(input.value));
                    state.colorName = selected?.name || "";
                    state.page = 1;
                    syncColorInputs();
                    renderActiveFilters();
                    updateUrl();
                    loadProducts();
                });
            });
        });
    }

    function renderProducts(products) {
        hideProductsStates();

        if (!Array.isArray(products) || products.length === 0) {
            elements.productsEmpty?.classList.remove("hidden");
            return;
        }

        elements.productsGrid.innerHTML = products.map(productCardTemplate).join("");
        elements.productsGrid.classList.remove("hidden");
    }

    function productCardTemplate(product) {
        const image = resolveMediaUrl(product.main_image);
        const price = Number(product.price || 0);
        const finalPrice = Number(product.final_price ?? product.price ?? 0);
        const discount = Number(product.discount_percent || 0);
        const stock = Number(product.stock || 0);
        const colors = Array.isArray(product.colors) ? product.colors : [];

        const colorDots = colors.length
            ? `<ul class="absolute top-4 start-3 space-y-1 z-10">${colors.slice(0, 4).map(color => `
                <li title="${escapeHtml(color.name)}" class="w-2.5 h-2.5 rounded-full border border-gray-300 dark:border-gray-600" style="background:${safeColor(color.hex_code)}"></li>
            `).join("")}</ul>`
            : "";

        const discountBadge = discount > 0
            ? `<div class="absolute end-3 top-3 bg-secondary-500 text-white text-xs font-bold px-2 py-1 rounded-xl rounded-bl-md shadow shadow-red-500/50 z-10">${toPersianDigits(discount)}٪</div>`
            : "";

        const stockBadge = stock <= 0
            ? `<div class="absolute end-3 top-3 bg-gray-600 text-white text-xs font-bold px-2 py-1 rounded-xl z-10">ناموجود</div>`
            : discountBadge;

        const priceBlock = stock <= 0
            ? `<span class="font-bold text-sm text-gray-500">ناموجود</span>`
            : `
                ${discount > 0 ? `<span class="text-xs text-gray-400 dark:text-gray-500 line-through tracking-wider text-left">${toPersianDigits(formatNumber(price))}</span>` : ""}
                <span class="font-bold text-sm text-gray-900 dark:text-gray-200 tracking-wider text-left">${toPersianDigits(formatNumber(finalPrice))} <span class="text-[11px] font-normal">تومان</span></span>
            `;

        // Frontend detail page is created in the next stage. Keep the slug ready in data-product-slug.
        return `
            <div class="lg:col-span-3 sm:col-span-6 col-span-12 w-full">
                <article class="relative h-full dark:border-gray-700 dark:shadow-[0_0_10px_rgba(0,0,0,0.6)] rounded p-3 bg-white dark:bg-custom-dark transition-all duration-200 ease-in-out group border border-transparent hover:border-gray-200 dark:hover:border-gray-700">
                    ${colorDots}
                    <div class="text-center flex items-center justify-center overflow-hidden h-44 rounded-lg bg-white dark:bg-custom-dark">
                        ${image
                            ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(product.name)}" loading="lazy" class="block h-40 max-w-full object-contain transition-transform duration-300 group-hover:scale-105">`
                            : productFallbackIcon()
                        }
                    </div>
                    ${stockBadge}
                    <div class="mt-3">
                        <h2 class="font-normal text-sm leading-6 h-12 mt-2 px-1 overflow-hidden group-hover:text-primary-600 dark:group-hover:text-primary-400 dark:text-gray-200 text-gray-900 transition-colors duration-200">
                            <button type="button" data-product-slug="${escapeHtml(product.slug || "")}" class="font-bold text-start line-clamp-2">${escapeHtml(product.name || "بدون نام")}</button>
                        </h2>
                        <p class="mt-1 px-1 text-[11px] text-gray-400 line-clamp-1">${escapeHtml(product.category || "")}</p>
                    </div>
                    <div class="mt-3 flex justify-end items-end min-h-12">
                        <div class="flex flex-col justify-end min-h-10 text-left">${priceBlock}</div>
                    </div>
                </article>
            </div>
        `;
    }

    function renderPagination() {
        if (!elements.productsPagination) return;

        const totalPages = Math.max(1, Math.ceil(state.total / PAGE_SIZE));
        if (state.total <= PAGE_SIZE) {
            elements.productsPagination.classList.add("hidden");
            elements.productsPagination.innerHTML = "";
            return;
        }

        if (state.page > totalPages) {
            state.page = totalPages;
        }

        const pageNumbers = paginationNumbers(state.page, totalPages);
        const pagesHtml = pageNumbers.map(page => {
            if (page === "…") {
                return `<span class="px-2 text-gray-400">…</span>`;
            }

            const active = page === state.page;
            return `<button type="button" data-page="${page}" class="flex items-center justify-center min-w-10 px-3 py-2.5 rounded-lg text-sm ${active ? "bg-primary text-white shadow-sm" : "text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-white/10"}">${toPersianDigits(page)}</button>`;
        }).join("");

        elements.productsPagination.innerHTML = `
            <button type="button" data-page="${state.page - 1}" ${state.page <= 1 ? "disabled" : ""} class="flex items-center gap-1.5 px-3.5 py-2.5 text-sm rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10 disabled:opacity-40 disabled:pointer-events-none">
                قبلی
            </button>
            <div class="flex items-center gap-2">${pagesHtml}</div>
            <button type="button" data-page="${state.page + 1}" ${state.page >= totalPages ? "disabled" : ""} class="flex items-center gap-1.5 px-3.5 py-2.5 text-sm rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10 disabled:opacity-40 disabled:pointer-events-none">
                بعدی
            </button>
        `;

        elements.productsPagination.classList.remove("hidden");
        elements.productsPagination.querySelectorAll("[data-page]").forEach(button => {
            button.addEventListener("click", () => {
                const nextPage = Number(button.dataset.page);
                if (!Number.isInteger(nextPage) || nextPage < 1 || nextPage > totalPages || nextPage === state.page) return;
                state.page = nextPage;
                updateUrl();

                if (state.clientSideProducts) {
                    const offset = (state.page - 1) * PAGE_SIZE;
                    renderProducts(state.clientSideProducts.slice(offset, offset + PAGE_SIZE));
                    renderPagination();
                    window.scrollTo({ top: productsTop(), behavior: "smooth" });
                } else {
                    loadProducts().then(() => window.scrollTo({ top: productsTop(), behavior: "smooth" }));
                }
            });
        });
    }

    function renderResultCount() {
        if (!elements.productsResultCount) return;
        elements.productsResultCount.textContent = `${toPersianDigits(formatNumber(state.total))} محصول`;
    }

    function renderActiveFilters() {
        const tags = [];

        if (state.search) tags.push({ key: "search", label: `جستجو: ${state.search}` });
        if (state.category) tags.push({ key: "category", label: `دسته: ${state.categoryName || state.category}` });
        if (state.color) tags.push({ key: "color", label: `رنگ: ${state.colorName || state.color}` });
        if (state.minPrice) tags.push({ key: "minPrice", label: `از ${toPersianDigits(formatNumber(state.minPrice))} تومان` });
        if (state.maxPrice) tags.push({ key: "maxPrice", label: `تا ${toPersianDigits(formatNumber(state.maxPrice))} تومان` });
        if (state.inStock) tags.push({ key: "inStock", label: "فقط موجودها" });

        elements.filterPanels.forEach(panel => {
            const container = panel.querySelector("[data-active-filters]");
            const emptyText = panel.querySelector("[data-no-active-filter]");
            if (!container) return;

            container.innerHTML = tags.map(tag => `
                <button type="button" data-remove-filter="${tag.key}" class="flex items-center gap-1 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl text-xs text-gray-700 dark:text-gray-200 hover:bg-primary hover:text-white hover:border-primary transition-all duration-200">
                    <span>${escapeHtml(tag.label)}</span>
                    <span aria-hidden="true">×</span>
                </button>
            `).join("");

            emptyText?.classList.toggle("hidden", tags.length > 0);

            container.querySelectorAll("[data-remove-filter]").forEach(button => {
                button.addEventListener("click", () => removeFilter(button.dataset.removeFilter));
            });
        });
    }

    function removeFilter(key) {
        if (key === "search") state.search = "";
        if (key === "category") { state.category = ""; state.categoryName = ""; }
        if (key === "color") { state.color = ""; state.colorName = ""; }
        if (key === "minPrice") state.minPrice = "";
        if (key === "maxPrice") state.maxPrice = "";
        if (key === "inStock") state.inStock = false;

        state.page = 1;
        syncControlsFromState();
        renderActiveFilters();
        updateSelectedCategoryCards();
        updateUrl();
        loadProducts();
    }

    function clearAllFilters() {
        state.search = "";
        state.category = "";
        state.categoryName = "";
        state.color = "";
        state.colorName = "";
        state.minPrice = "";
        state.maxPrice = "";
        state.inStock = false;
        state.page = 1;

        syncControlsFromState();
        renderActiveFilters();
        updateSelectedCategoryCards();
        updateUrl();
        loadProducts();
    }

    function syncControlsFromState() {
        elements.filterPanels.forEach(panel => {
            const search = panel.querySelector("[data-filter-search]");
            const min = panel.querySelector("[data-min-price]");
            const max = panel.querySelector("[data-max-price]");
            const inStock = panel.querySelector("[data-in-stock]");

            if (search) search.value = state.search;
            if (min) min.value = state.minPrice;
            if (max) max.value = state.maxPrice;
            if (inStock) inStock.checked = state.inStock;
        });

        syncColorInputs();
    }

    function syncSearchInputs(source) {
        elements.filterPanels.forEach(panel => {
            const input = panel.querySelector("[data-filter-search]");
            if (input && input !== source) input.value = state.search;
        });
    }

    function syncPriceInputs() {
        elements.filterPanels.forEach(panel => {
            const min = panel.querySelector("[data-min-price]");
            const max = panel.querySelector("[data-max-price]");
            if (min) min.value = state.minPrice;
            if (max) max.value = state.maxPrice;
        });
    }

    function syncInStockInputs(source) {
        elements.filterPanels.forEach(panel => {
            const input = panel.querySelector("[data-in-stock]");
            if (input && input !== source) input.checked = state.inStock;
        });
    }

    function syncColorInputs() {
        elements.filterPanels.forEach(panel => {
            panel.querySelectorAll("[data-color-options] input").forEach(input => {
                input.checked = String(input.value) === String(state.color);
            });
        });
    }

    function setActiveSortButton() {
        elements.sortButtons.forEach(button => {
            button.classList.toggle("is-active", (button.dataset.ordering || "") === state.ordering);
        });
    }

    function restoreStateFromUrl() {
        const params = new URLSearchParams(window.location.search);
        state.search = params.get("search") || "";
        state.category = params.get("category") || "";
        state.color = params.get("color") || "";
        state.minPrice = params.get("min_price") || "";
        state.maxPrice = params.get("max_price") || "";
        state.inStock = params.get("in_stock") === "true";
        state.ordering = params.get("ordering") || "";
        state.page = Math.max(1, Number(params.get("page") || 1));
    }

    function updateUrl() {
        const params = new URLSearchParams();
        if (state.search) params.set("search", state.search);
        if (state.category) params.set("category", state.category);
        if (state.color) params.set("color", state.color);
        if (state.minPrice) params.set("min_price", state.minPrice);
        if (state.maxPrice) params.set("max_price", state.maxPrice);
        if (state.inStock) params.set("in_stock", "true");
        if (state.ordering) params.set("ordering", state.ordering);
        if (state.page > 1) params.set("page", String(state.page));

        const newUrl = params.toString()
            ? `${window.location.pathname}?${params.toString()}`
            : window.location.pathname;
        window.history.replaceState({}, "", newUrl);
    }

    function showProductsLoading() {
        hideProductsStates();
        elements.productsLoading?.classList.remove("hidden");
    }

    function showProductsError() {
        hideProductsStates();
        elements.productsError?.classList.remove("hidden");
    }

    function hideProductsStates() {
        elements.productsLoading?.classList.add("hidden");
        elements.productsGrid?.classList.add("hidden");
        elements.productsError?.classList.add("hidden");
        elements.productsEmpty?.classList.add("hidden");
    }

    async function fetchJson(url, options = {}) {
        const response = await fetch(url, {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
            ...options,
        });

        if (!response.ok) {
            const error = new Error(`Request failed: ${response.status}`);
            error.status = response.status;
            throw error;
        }

        return response.json();
    }

    function normalizeListResponse(response) {
        if (Array.isArray(response)) return response;
        if (Array.isArray(response?.results)) return response.results;
        return [];
    }

    function normalizePriceValue(value) {
        const number = Number(String(value ?? "").replace(/,/g, ""));
        return Number.isFinite(number) && number > 0 ? String(Math.round(number)) : "";
    }

    function resolveMediaUrl(value) {
        if (!value) return "";
        try {
            return new URL(value, window.location.origin).href;
        } catch {
            return value;
        }
    }

    function formatNumber(value) {
        const number = Number(value || 0);
        return Number.isFinite(number) ? new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(number) : "0";
    }

    function toPersianDigits(value) {
        const map = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
        return String(value).replace(/\d/g, digit => map[Number(digit)]);
    }

    function safeColor(value) {
        const color = String(value || "").trim();
        return /^#[0-9a-fA-F]{6}$/.test(color) ? color : "#d1d5db";
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function paginationNumbers(current, total) {
        if (total <= 7) return Array.from({ length: total }, (_, index) => index + 1);

        const pages = [1];
        if (current > 4) pages.push("…");

        const start = Math.max(2, current - 1);
        const end = Math.min(total - 1, current + 1);
        for (let page = start; page <= end; page += 1) pages.push(page);

        if (current < total - 3) pages.push("…");
        pages.push(total);
        return pages;
    }

    function productsTop() {
        return Math.max(0, (document.getElementById("sortButtons")?.getBoundingClientRect().top || 0) + window.scrollY - 120);
    }

    function categoryFallbackIcon() {
        return `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.3" stroke="currentColor" class="size-10 text-gray-400">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"/>
            </svg>
        `;
    }

    function productFallbackIcon() {
        return `
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.2" stroke="currentColor" class="size-20 text-gray-300">
                <path stroke-linecap="round" stroke-linejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909m-18 3.75h16.5a1.5 1.5 0 0 0 1.5-1.5V6a1.5 1.5 0 0 0-1.5-1.5H3.75A1.5 1.5 0 0 0 2.25 6v12a1.5 1.5 0 0 0 1.5 1.5Zm10.5-11.25h.008v.008h-.008V8.25Z"/>
            </svg>
        `;
    }
})();

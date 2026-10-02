(() => {
    "use strict";
    const apiRoot = "/api/v1/";
    const number = value => new Intl.NumberFormat("fa-IR", { maximumFractionDigits: 0 }).format(Number(value) || 0);
    const productUrl = product => "/products/" + encodeURIComponent(product.slug) + "/";
    const categoryUrl = category => "/products/?category=" + encodeURIComponent(category.id);

    document.addEventListener("DOMContentLoaded", async () => {
        const [categoryResult, productResult] = await Promise.allSettled([
            fetchAll(apiRoot + "categories/?limit=100"),
            fetchAll(apiRoot + "products/?ordering=-created_at"),
        ]);
        if (categoryResult.status === "fulfilled") renderCategories(categoryResult.value);
        else status("homeCategoriesStatus", "بارگذاری دسته‌بندی‌ها انجام نشد. صفحه را دوباره بارگذاری کنید.");
        if (productResult.status === "fulfilled") renderProducts(productResult.value);
        else ["homeHeroStatus", "homeDiscountStatus", "homeLatestStatus"].forEach(id =>
            status(id, "بارگذاری محصولات انجام نشد. صفحه را دوباره بارگذاری کنید."));
        if (categoryResult.status === "fulfilled" && productResult.status === "fulfilled")
            renderGroups(categoryResult.value, productResult.value);
        else status("homeGroupsStatus", "بارگذاری محصولات دسته‌بندی‌ها انجام نشد.");
    });

    async function fetchAll(path) {
        const items = [];
        let next = path;
        while (next) {
            const url = new URL(next, window.location.origin);
            if (url.origin !== window.location.origin || !url.pathname.startsWith(apiRoot))
                throw new Error("Unexpected API URL");
            const response = await fetch(url.href, { credentials: "same-origin", headers: { Accept: "application/json" } });
            if (!response.ok) throw new Error("API request failed: " + response.status);
            const data = await response.json();
            if (Array.isArray(data)) { items.push(...data); break; }
            if (!Array.isArray(data.results)) throw new Error("Unexpected API response");
            items.push(...data.results);
            next = data.next;
        }
        return items;
    }

    function renderCategories(categories) {
        if (!categories.length) { status("homeCategoriesStatus", "دسته‌بندی فعالی ثبت نشده است."); return; }
        document.getElementById("homeCategoriesSlides").innerHTML = categories.map(category => {
            const image = media(category.image);
            return '<div class="swiper-slide !size-40"><a href="' + categoryUrl(category) +
                '" class="bg-white dark:bg-custom-dark dark:border-gray-700 space-y-3 shadow-sm border border-gray-200 p-3 rounded-2xl flex flex-col items-center justify-center hover:shadow-md transition-all w-full h-full">' +
                '<figure class="w-20 h-20 flex items-center justify-center">' +
                (image ? '<img src="' + escapeHtml(image) + '" alt="" class="max-w-full max-h-full object-contain" loading="lazy">' :
                    '<span class="text-3xl text-primary" aria-hidden="true">✎</span>') +
                '</figure><h3 class="text-sm font-medium text-gray-900 dark:text-gray-200 text-center line-clamp-2">' +
                escapeHtml(category.name) + '</h3></a></div>';
        }).join("");
        hideStatus("homeCategoriesStatus");
        showCarousel("homeCategoriesCarousel");
    }

    function renderProducts(products) {
        const latest = products.slice(0, 10);
        const discounted = products.filter(item => Number(item.discount_percent) > 0 && Number(item.stock) > 0).slice(0, 10);
        if (latest.length) {
            document.getElementById("homeHeroSlides").innerHTML = latest.slice(0, 3).map(heroSlide).join("");
            document.getElementById("homeLatestSlides").innerHTML = latest.map(slide).join("");
            hideStatus("homeHeroStatus");
            hideStatus("homeLatestStatus");
            showCarousel("homeHero");
            showCarousel("homeLatestCarousel");
        } else {
            status("homeHeroStatus", "هنوز محصولی ثبت نشده است.");
            status("homeLatestStatus", "هنوز محصولی ثبت نشده است.");
        }
        if (discounted.length) {
            document.getElementById("homeDiscountSlides").innerHTML = discounted.map(discountSlide).join("");
            hideStatus("homeDiscountStatus");
            showCarousel("homeDiscountCarousel");
        } else status("homeDiscountStatus", "فعلاً محصول تخفیف‌دار موجود نیست.");
    }

    function renderGroups(categories, products) {
        const groups = categories.map(category => ({
            category, items: products.filter(product => product.category === category.name).slice(0, 4),
        })).filter(group => group.items.length).slice(0, 3);
        if (!groups.length) { status("homeGroupsStatus", "هنوز محصولی برای دسته‌بندی‌ها ثبت نشده است."); return; }
        document.getElementById("homeCategoryGroups").innerHTML = groups.map(group =>
            '<section class="lg:col-span-6 xl:col-span-4 col-span-12 w-full bg-white dark:bg-custom-dark rounded-2xl p-3 drop-shadow">' +
            '<header class="flex items-center justify-between p-2"><h3 class="font-bold text-lg dark:text-gray-200">' +
            escapeHtml(group.category.name) + '</h3><a href="' + categoryUrl(group.category) +
            '" class="text-xs font-medium bg-primary text-white py-1.5 px-4 rounded-lg">بیشتر</a></header>' +
            '<div class="grid grid-cols-2 gap-2">' + group.items.map(card).join("") + '</div></section>'
        ).join("");
        hideStatus("homeGroupsStatus");
    }

    function heroSlide(product) {
        const image = media(product.main_image);
        return '<div class="swiper-slide"><a href="' + productUrl(product) +
            '" class="block bg-primary dark:bg-custom-dark rounded-2xl p-6 sm:p-10">' +
            '<div class="grid md:grid-cols-2 gap-6 items-center min-h-64"><div class="text-white">' +
            '<span class="text-sm opacity-80">' + escapeHtml(product.category) + '</span>' +
            '<h2 class="text-2xl sm:text-3xl font-black leading-10 mt-3">' + escapeHtml(product.name) + '</h2>' +
            '<p class="font-bold mt-5">' + price(product) + '</p>' +
            '<span class="inline-block bg-white text-primary font-bold text-sm px-5 py-2 rounded-lg mt-5">مشاهده محصول</span></div>' +
            '<div class="h-64 flex items-center justify-center bg-white rounded-xl p-5">' +
            (image ? '<img src="' + escapeHtml(image) + '" alt="' + escapeHtml(product.name) +
                '" class="max-h-full max-w-full object-contain" loading="lazy">' : '<span class="text-gray-400">بدون تصویر</span>') +
            '</div></div></a></div>';
    }

    function discountSlide(product) { return '<div class="swiper-slide !w-60 h-auto">' + card(product) + '</div>'; }
    function slide(product) { return '<div class="swiper-slide h-auto">' + card(product) + '</div>'; }
    function card(product) {
        const image = media(product.main_image);
        const discount = Number(product.discount_percent) || 0;
        return '<a href="' + productUrl(product) +
            '" class="group relative block h-full bg-white dark:bg-custom-dark rounded-xl p-3 border border-gray-200 dark:border-gray-700 hover:border-primary transition-colors">' +
            (discount > 0 && Number(product.stock) > 0 ?
                '<span class="absolute end-3 top-3 bg-secondary-500 text-white text-xs font-bold px-2 py-1 rounded-xl z-10">' +
                number(discount) + '٪</span>' : '') +
            '<div class="flex items-center justify-center overflow-hidden h-36">' +
            (image ? '<img src="' + escapeHtml(image) + '" alt="' + escapeHtml(product.name) +
                '" loading="lazy" class="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform">' :
                '<span class="text-gray-400 text-xs">بدون تصویر</span>') +
            '</div><h3 class="font-bold text-sm leading-6 h-12 mt-3 overflow-hidden text-gray-900 dark:text-gray-200 line-clamp-2">' +
            escapeHtml(product.name) + '</h3><div class="mt-3 text-end text-sm font-bold text-gray-900 dark:text-gray-200">' +
            price(product) + '</div></a>';
    }
    function price(product) {
        if (Number(product.stock) <= 0) return "ناموجود";
        return (Number(product.discount_percent) > 0 ?
            '<del class="opacity-60 text-xs me-2">' + number(product.price) + '</del>' : '') +
            '<span>' + number(product.final_price ?? product.price) + ' تومان</span>';
    }
    function media(value) {
        if (!value) return "";
        try {
            const url = new URL(value, window.location.origin);
            return ["http:", "https:"].includes(url.protocol) ? url.href : "";
        } catch { return ""; }
    }
    function escapeHtml(value) {
        return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
    }
    function status(id, message) { document.getElementById(id).textContent = message; }
    function hideStatus(id) { document.getElementById(id).classList.add("hidden"); }
    function showCarousel(id) {
        const carousel = document.getElementById(id);
        carousel.classList.remove("hidden");
        requestAnimationFrame(() => carousel.swiper?.update());
    }
})();
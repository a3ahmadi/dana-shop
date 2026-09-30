
const swiper = new Swiper(".default-carousel", {
    loop: true,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    autoplay: {
        delay: 3000,
    },
});

const customSwiperNext = document.querySelector('.custom-swiper-next');
const customSwiperPrev = document.querySelector('.custom-swiper-prev');

if (customSwiperNext  || customSwiperPrev) {
    customSwiperNext.addEventListener('click',()=>{
        swiper.slideNext()
    })

    customSwiperPrev.addEventListener('click',()=>{
        swiper.slidePrev()
    })
}

new Swiper(".amazing-carousel", {
    slidesPerView: "auto",
    spaceBetween: 1,
    freeMode: true,
    navigation: {
        nextEl: ".swiper-button-next-amazing",
        prevEl: ".swiper-button-prev-amazing",
    }
});

new Swiper(".landing-amazing-carousel", {
    slidesPerView: 2,
    spaceBetween: 10,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    breakpoints: {
        100: { slidesPerView: 1 },
        576: { slidesPerView: 2 },
        768: { slidesPerView: 3 },
        1024: { slidesPerView: 4 },
    },
});

new Swiper(".category-carousel", {
    slidesPerView: 5,
    spaceBetween: 30,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
});

new Swiper(".product-carousel", {
    slidesPerView: 5,
    spaceBetween: 2,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    autoplay: {
        delay: 3000,
    },
    breakpoints: {
        100: { slidesPerView: 1 },
        576: { slidesPerView: 2 },
        768: { slidesPerView: 3 },
        1024: { slidesPerView: 5 },
        1400: { slidesPerView: 6 }
    },
});

new Swiper(".product-list-carousel", {
    slidesPerView: 5,
    spaceBetween: 10,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    autoplay: {
        delay: 3000,
    },
    breakpoints: {
        100: { slidesPerView: 1 },
        576: { slidesPerView: 2 },
        1200: { slidesPerView: 4 },
    },
});


new Swiper(".blog-carousel", {
    slidesPerView: 5,
    spaceBetween: 10,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    breakpoints: {
        100: { slidesPerView: 1 },
        576: { slidesPerView: 2 },
        992: { slidesPerView: 4 },
        1200: { slidesPerView: 5 },
    },
    autoplay: {
        delay: 3000,
    },
});


var swiperProductGalleryOne= new Swiper("#productGalleryOne", {
    spaceBetween: 10,
    slidesPerView: 3,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
});
var swiperProductGalleryTwo=new Swiper("#productGalleryTwo", {
    spaceBetween: 10,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    thumbs: {
        swiper: swiperProductGalleryOne,
    },
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
    zoom: true,
});


new Swiper(".free-mode", {
    slidesPerView: "auto",
    spaceBetween: 10,
    freeMode: true,
    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },
    autoplay: {
        delay: 3000,
    },
});

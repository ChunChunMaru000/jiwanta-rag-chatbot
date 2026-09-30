document.addEventListener("DOMContentLoaded", () => {

// ==============================
// NAVBAR MOBILE MENU
// ==============================
const navLinks = document.querySelectorAll(".nav-menu .nav-link");
const menuOpenButton = document.querySelector("#menu-open-button");
const menuCloseButton = document.querySelector("#menu-close-button");

if (menuOpenButton) {
    menuOpenButton.addEventListener("click", () => {
        document.body.classList.toggle("show-mobile-menu");
    });
}

if (menuCloseButton) {
    menuCloseButton.addEventListener("click", () => menuOpenButton.click());
}

navLinks.forEach(link => {
    link.addEventListener("click", () => {
        if (document.body.classList.contains("show-mobile-menu")) {
            menuOpenButton.click();
        }
    });
});


// ==============================
// FILTER TAB (MENU)
// ==============================
const filterTabs = document.querySelectorAll(".filter-tab");
const productItems = document.querySelectorAll(".product-item");

filterTabs.forEach(tab => {
    tab.addEventListener("click", () => {
        filterTabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");

        const filter = tab.dataset.filter;
        productItems.forEach(item => {
            if (filter === "all" || item.dataset.category === filter) {
                item.style.display = "flex";
                item.style.animation = "fadeIn 0.3s ease";
            } else {
                item.style.display = "none";
            }
        });
    });
});


// ==============================
// SWIPER SLIDER
// ==============================
if (document.querySelector('.slider-wrapper')) {
    const swiper = new Swiper('.slider-wrapper', {
        loop: true,
        grabCursor: true,
        spaceBetween: 25,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
            dynamicBullets: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        breakpoints: {
            0: { slidesPerView: 1 },
            768: { slidesPerView: 2 },
            1024: { slidesPerView: 3 }
        }
    });
}

}); // end DOMContentLoaded


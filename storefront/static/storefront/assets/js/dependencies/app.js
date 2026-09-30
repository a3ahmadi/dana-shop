/**
 * CITY SELECTOR MODULE v1
 * Designed by Amir Rezae
 * Features:
 * - Tag management system
 * - Live search filtering
 * - State synchronization
 * - Query string generation
 */

document.addEventListener('DOMContentLoaded', () => {
    // Configuration
    const config = {
        container: document.getElementById('citySelector'),
        searchForm: document.getElementById('searchForm'),
        cityList: document.getElementById('cityList'),
        selectedCitiesContainer: document.getElementById('selectedCities'),
        filterButton: document.getElementById('filterButton')
    };

    // Initial Data
    let selectedCities = new Set();
    const cities = config.container ? config.container.dataset.cities.split(',') : []; // Check if container exists

    // Ensure required elements exist before initialization
    if (!config.cityList || !config.selectedCitiesContainer || !config.searchForm) {
        return;
    }

    // Initialize Module
    initCitySelector();

    function initCitySelector() {
        setupSearch();
        setupFilterButton();
        renderCityList();
    }

    function setupSearch() {
        const searchInput = document.getElementById('search');
        if (!searchInput) return; // Ensure input exists

        searchInput.addEventListener('input', (e) => {
            renderCityList(e.target.value);
        });

        config.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    }

    function renderCityList(filter = '') {
        config.cityList.innerHTML = '';

        cities
            .filter(city => city.includes(filter))
            .forEach(city => {
                const listItem = createCityListItem(city);
                config.cityList.appendChild(listItem);
            });
    }

    function createCityListItem(city) {
        const li = document.createElement('li');
        li.className = 'w-full border-b border-gray-200 rounded-t-lg dark:border-gray-600';

        const checkboxId = `city-${city.replace(/\s/g, '-')}`;
        const isChecked = selectedCities.has(city);

        li.innerHTML = `
            <div class="flex items-center ps-3">
                <input 
                    id="${checkboxId}" 
                    type="checkbox" 
                    ${isChecked ? 'checked' : ''}
                    class="city-checkbox w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600"
                >
                <label 
                    for="${checkboxId}" 
                    class="w-full py-3 ms-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                >
                    ${city}
                </label>
            </div>
        `;

        const checkbox = li.querySelector('input');
        if (checkbox) {
            checkbox.addEventListener('change', (e) => {
                handleCitySelection(city, e.target.checked);
            });
        }

        return li;
    }

    function handleCitySelection(city, isSelected) {
        if (isSelected) {
            selectedCities.add(city);
        } else {
            selectedCities.delete(city);
        }
        renderSelectedTags();
    }

    function renderSelectedTags() {
        config.selectedCitiesContainer.innerHTML = '';

        selectedCities.forEach(city => {
            const tag = document.createElement('div');
            tag.className = 'flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full dark:bg-blue-900 dark:text-blue-200';
            tag.innerHTML = `
                ${city}
                <button 
                    type="button" 
                    class="ms-2 text-blue-600 cursor-pointer hover:text-blue-800 dark:text-blue-200 dark:hover:text-blue-400 remove-tag"
                    data-city="${city}"
                >
                    &times;
                </button>
            `;

            config.selectedCitiesContainer.appendChild(tag);
        });

        document.querySelectorAll('.remove-tag').forEach(btn => {
            btn.addEventListener('click', () => removeCityTag(btn.dataset.city));
        });
    }

    function removeCityTag(city) {
        selectedCities.delete(city);
        renderSelectedTags();

        document.querySelectorAll('.city-checkbox').forEach(checkbox => {
            const labelText = checkbox.nextElementSibling.textContent.trim();
            if (labelText === city) {
                checkbox.checked = false;
                checkbox.dispatchEvent(new Event('change'));
            }
        });
    }

    function setupFilterButton() {
        if (!config.filterButton) return;

        config.filterButton.addEventListener('click', () => {
            const queryString = Array.from(selectedCities)
                .map(city => encodeURIComponent(city))
                .join(',');

            window.location.href = `/results?cities=${queryString}`;
        });
    }
});


/**
 * MODAL MANAGER MODULE v1
 * Designed by Amir Rezae
 * Features:
 * - Dynamic modal handling
 * - Click-outside detection
 * - Multiple modal support
 */

document.addEventListener('DOMContentLoaded', () => {

    const navMenuMobile = document.getElementById('navMenuMobile');

    // Open modal
    document.querySelectorAll('.modal-trigger').forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modalTarget;
            const modal = document.querySelector(`[data-modal-id="${modalId}"]`);

            // Hide all modals before opening the target one
            document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));

            // Show the selected modal
            modal.classList.remove('hidden');

            // Hide mobile navigation menu when modal opens
            if (navMenuMobile) navMenuMobile.classList.add('hidden');
        });
    });

    // Close modal
    document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            const modal = closeBtn.closest('.modal');
            modal.classList.add('hidden');

            // Show mobile navigation menu when modal closes
            if (navMenuMobile) navMenuMobile.classList.remove('hidden');
        });
    });

    // Close when clicking outside
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                // Show mobile navigation menu when modal closes
                if (navMenuMobile) navMenuMobile.classList.remove('hidden');
            }
        });
    });
});


/**
 * MEGA MENU MODULE v1
 * Designed by Amir Rezae
 * Features:
 * - Desktop hover interactions
 * - Mobile toggle functionality
 * - Visual feedback states
 * - Cross-element synchronization
 */


// Select all elements with [data-mega-id] (hoverable menu items)
const dataMegaId = document.querySelectorAll("[data-mega-id]");

// Select all elements with [data-mega-target] (target dropdowns)
const dataMegaTarget = document.querySelectorAll("[data-mega-target]");

dataMegaId.forEach(item => {
    item.addEventListener("mouseenter", () => {
        const targetId = item.getAttribute("data-mega-id");

        // Remove 'bg-gray-100' class from all [data-mega-id] elements
        dataMegaId.forEach(el => el.classList.remove("bg-gray-100"));

        // Add 'bg-gray-100' class only to the hovered item
        item.classList.add("bg-gray-100");

        // Hide all [data-mega-target] elements
        dataMegaTarget.forEach(target => target.classList.add("hidden"));

        // Find and show the matching target element
        const matchedTarget = document.querySelector(`[data-mega-target="${targetId}"]`);
        if (matchedTarget) {
            matchedTarget.classList.remove("hidden");
        }
    });
});

// Select the menu trigger and the target menu
const megaMenuFire = document.getElementById('mega-menu-fire');
const megaMenuFireTarget = document.getElementById('mega-menu-fire-target');

// Check if elements exist to avoid errors
if (megaMenuFire && megaMenuFireTarget) {
    // Show the menu when the mouse enters the trigger element
    megaMenuFire.addEventListener('mouseover', () => {
        megaMenuFireTarget.classList.add('block');  // Make the menu visible
        megaMenuFireTarget.classList.remove('hidden'); // Remove the hidden class
    });

    // Hide the menu when the mouse leaves both the trigger and the menu
    document.addEventListener('mousemove', (event) => {
        // Check if the mouse is outside both elements
        if (!megaMenuFire.contains(event.target) && !megaMenuFireTarget.contains(event.target)) {
            megaMenuFireTarget.classList.add('hidden'); // Hide the menu
            megaMenuFireTarget.classList.remove('block'); // Ensure it is fully hidden
        }
    });
}


/**
 * Responsive Mega Menu
 * Toggles the visibility of a dropdown menu and rotates the corresponding icon.
 * @param {string} id - The ID of the dropdown menu to toggle.
 */
function toggleDropdown(id) {
    let menu = document.getElementById(id);


    let icon = document.getElementById('icon-' + id);

    // Only toggle if the element exists
    if (menu) {
        menu.classList.toggle('hidden');
    }

    if (icon) {
        icon.classList.toggle('rotate-180');
    }
}


/**
 * USAGE:
 * - Desktop: data-mega-id + data-mega-target attributes
 * - Mobile: onclick="megaMenu.toggleDropdown('menu-id')"
 * - Icons require ID pattern: icon-{menu-id}
 */


/**
 * OFF-CANVAS COMPONENT MODULE
 * Designed by Amir Rezae
 * Features:
 * - Position-aware animations (top/bottom/left/right)
 * - Overlay management
 * - Smooth transition effects
 * - Auto-close functionality
 */


// Function to toggle the offcanvas (open it)
function toggleOffcanvas(id) {
    // Get the offcanvas element by its ID
    let offcanvas = document.getElementById(id);
    // Get the overlay element
    let overlay = document.querySelector(".overlay");

    // Remove any previous translation or opacity classes
    offcanvas.classList.remove("translate-x-full", "-translate-x-full", "-translate-y-full", "translate-y-full", "opacity-0");

    // Add the class to make the offcanvas visible (full opacity)
    offcanvas.classList.add("opacity-100");
    offcanvas.classList.add("visible");
    offcanvas.classList.remove("invisible");

    // Show the overlay by removing the 'hidden' class
    overlay.classList.remove("hidden");
}

// Function to close all offcanvas elements
function closeOffcanvas() {
    // Loop through all elements with the class 'offcanvas'
    document.querySelectorAll(".offcanvas").forEach(el => {
        // Add opacity-0 to hide the offcanvas
        el.classList.add("opacity-0");

        // Check if the offcanvas is on the right and add corresponding translation class
        if (el.id.includes("right")) el.classList.add("translate-x-full");

        // Check if the offcanvas is on the left and add corresponding translation class
        if (el.id.includes("left")) el.classList.add("-translate-x-full");

        // Check if the offcanvas is at the top and add corresponding translation class
        if (el.id.includes("top")) el.classList.add("-translate-y-full");

        // Check if the offcanvas is at the bottom and add corresponding translation class
        if (el.id.includes("bottom")) el.classList.add("translate-y-full");

    });

    // Set a timeout to hide the overlay after 300ms to allow the animation to complete
    setTimeout(() => {
        // Add the 'hidden' class to the overlay to hide it
        document.querySelector(".overlay").classList.add("hidden");
    }, 300);
}

/**
 * STICKY MEGA MENU MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Hides mega menu when scrolling down
 * - Reappears when scrolling up
 * - Includes minimum scroll difference trigger
 */

// Wait for the DOM to fully load before executing the script
document.addEventListener("DOMContentLoaded", function () {
    let lastScrollTop = 0; // Store the last scroll position
    const delta = 100; // Threshold to detect significant scrolling
    const megaMenu = document.querySelector("#megaMenu"); // Select the mega menu element
    const header = document.querySelector("#topHeader"); // Select the header element

    if (!megaMenu || !header) return; // Exit if required elements are missing

    // Attach an event listener to detect scroll events
    window.addEventListener("scroll", function () {
        let nowScrollTop = window.scrollY || document.documentElement.scrollTop; // Get the current scroll position

        // Skip updates if the scroll change is too small
        if (Math.abs(lastScrollTop - nowScrollTop) < delta) {
            return;
        }

        if (nowScrollTop > lastScrollTop) {
            // User is scrolling down: Hide mega menu and apply shadow to header
            megaMenu.style.display = "none"; // Hide the mega menu
        } else {
            // User is scrolling up: Show mega menu and remove shadow from header
            megaMenu.removeAttribute("style"); // Reset any custom styles
        }

        lastScrollTop = nowScrollTop; // Update the last known scroll position
    });
});


/**
 * DARK MODE TOGGLE MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Reads system dark mode preference if no saved preference exists
 * - Checks and applies saved dark mode preference
 * - Toggles dark mode on button click
 */

document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("dark-mode-toggle");
    const htmlElement = document.documentElement;

    // Read saved preference OR fallback to system preference
    const savedTheme = localStorage.getItem("theme");
    const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    if (savedTheme === "dark" || (!savedTheme && systemPrefersDark)) {
        htmlElement.classList.add("dark");
    } else {
        htmlElement.classList.remove("dark");
    }

    // Watch for system changes in real time
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem("theme")) {
            if (e.matches) {
                htmlElement.classList.add("dark");
            } else {
                htmlElement.classList.remove("dark");
            }
        }
    });

    // Toggle theme on click
    if (toggleButton) {
        toggleButton.addEventListener("click", function () {
            if (htmlElement.classList.contains("dark")) {
                htmlElement.classList.remove("dark");
                localStorage.setItem("theme", "light");
            } else {
                htmlElement.classList.add("dark");
                localStorage.setItem("theme", "dark");
            }
        });
    }
});



/**
 * COUNTER CART MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows incrementing and decrementing item counts in a shopping cart
 * - Prevents item count from dropping below 1 during decrement
 */

/**
 * Decrements the item count
 * @param id - The ID of the element displaying the count
 */
function decrement(id) {
    let countElement = document.getElementById(id); // Get the element by its ID
    let count = parseInt(countElement.innerText); // Parse the current count as an integer
    if (count > 1) {
        countElement.innerText = count - 1; // Decrease the count by 1 (if greater than 1)
    }
}

/**
 * Increments the item count
 * @param id - The ID of the element displaying the count
 */
function increment(id) {
    let countElement = document.getElementById(id); // Get the element by its ID
    let count = parseInt(countElement.innerText); // Parse the current count as an integer
    countElement.innerText = count + 1; // Increase the count by 1
}


/**
 * TOGGLE TEXT MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Toggles the visibility of additional text on user interaction
 * - Updates the button text dynamically based on the state
 * - Ensures a seamless user experience for reading more content
 */

function toggleText() {
    var extraText = document.getElementById("extra-text"); // Get the additional text element by its ID
    var btn = document.getElementById("toggle-btn"); // Get the toggle button by its ID

    // Check the current display state of the extra text
    if (extraText.style.display === "none") {
        extraText.style.display = "inline"; // Show the extra text
        btn.textContent = "بستن ادامه مطلب"; // Update button text to "Close Read More"
    } else {
        extraText.style.display = "none"; // Hide the extra text
        btn.textContent = "ادامه مطلب"; // Update button text to "Read More"
    }
}

/**
 * RATING MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Dynamically updates star ratings based on user selection
 * - Ensures a visually interactive and engaging rating experience
 * - Handles both stars and their corresponding label styles seamlessly
 */

document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll('input[name="rating"]'); // Select all rating input elements
    const labels = document.querySelectorAll('label svg'); // Select all SVG elements within labels

    // Ensure both stars and labels are present before adding logic
    if (stars.length > 0 && labels.length > 0) {
        stars.forEach((star, index) => {
            star.addEventListener('change', () => {
                // Update the styles of the labels based on the selected star
                labels.forEach((label, i) => {
                    label.classList.toggle('text-orange-300', i <= index); // Highlight selected stars
                    label.classList.toggle('text-gray-400', i > index);   // Dim unselected stars
                });
            });
        });
    }
});


/**
 * TAG INPUT MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows users to dynamically create and style tags
 * - Handles both default and custom colors for each tag
 * - Ensures seamless interaction and efficient tag management
 */

(function initTagInputs() {
    const containers = document.querySelectorAll('.tag-container'); // Select all tag input containers

    containers.forEach(container => {
        const input = container.querySelector('.tag-input'); // Find the input element within the container
        if (!input) return; // Skip if no input is found

        const colors = ['bg-pink-200', 'bg-green-200', 'bg-purple-200', 'bg-blue-200', 'bg-yellow-200']; // Predefined colors
        let colorIndex = 0;

        // Retrieve default color from the data attribute or use the first predefined color
        const defaultColor = input.dataset.color || colors[0];
        const isHexColor = defaultColor?.startsWith('#'); // Check if the default color is a HEX value

        // Add event listener to handle Enter keypress
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && input.value.trim()) {
                e.preventDefault(); // Prevent form submission
                createTag(input.value.trim(), container); // Create a new tag with the entered value
                input.value = ''; // Clear the input field
            }
        });

        function createTag(fullText, container) {
            const [text, customColor] = fullText.split('#'); // Separate text and custom color if provided
            const tag = document.createElement('div'); // Create a new tag element

            // Manage the tag's background color
            let tagColor = '';
            if (customColor) {
                tag.style.backgroundColor = `#${customColor}`; // Apply custom color if provided
            } else {
                if (isHexColor) {
                    tag.style.backgroundColor = defaultColor; // Apply HEX default color
                } else {
                    tagColor = defaultColor; // Apply class-based default color
                    colorIndex = (colorIndex + 1) % colors.length; // Cycle through predefined colors
                }
            }

            tag.className = `flex items-center px-3 py-1 rounded-full text-sm text-gray-700 ${tagColor}`; // Assign styling classes

            tag.innerHTML = `
                <span>${text}</span>
                <button 
                    type="button" 
                    class="mr-2 hover:text-red-600 transition-colors"
                    onclick="this.parentElement.remove()"
                >
                    &times;
                </button>
            `;

            container.insertBefore(tag, input); // Insert the created tag before the input field
        }
    });
})();


/**
 * ACCORDION MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Expands and collapses content panels on button click
 * - Toggles accordion icon rotation for visual feedback
 * - Uses utility classes for smooth height transitions
 */

document.querySelectorAll('.accordion-btn').forEach(button => {
    button.addEventListener('click', () => {
        const content = button.nextElementSibling; // Get the content section next to the button
        const icon = button.querySelector('.svg-accordion'); // Get the accordion icon within the button

        button.classList.toggle('active'); // Toggle active state on button
        content.classList.toggle('max-h-0'); // Collapse if open
        content.classList.toggle('max-h-[500px]'); // Expand if closed

        // Rotate icon if it exists
        if (icon) {
            icon.classList.toggle('rotate-180');
        }
    });
});


/**
 * PRICE RANGE MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Custom dual-range slider to select minimum and maximum prices
 * - Syncs visual slider with formatted Persian inputs
 * - Handles mouse interactions with smooth updates
 * - Prevents overlap between min and max thumbs
 */

class DualRangeSlider {
    constructor(container, options = {}) {
        this.container = container;
        this.min = options.min || 0;
        this.max = options.max || 1000000;
        this.minValue = options.initialMin || this.min;
        this.maxValue = options.initialMax || this.max;

        // Select DOM elements inside the container
        this.minThumb = this.container.querySelector('.min-thumb');
        this.maxThumb = this.container.querySelector('.max-thumb');
        this.range = this.container.querySelector('.slider-range');
        this.track = this.container.querySelector('.slider-track');
        this.minInput = this.container.querySelector('.min-input');
        this.maxInput = this.container.querySelector('.max-input');

        this.validateValues(); // Ensure initial values are within bounds
        this.init(); // Initialize slider
    }

    validateValues() {
        // Clamp values within allowed range
        this.minValue = Math.max(this.min, Math.min(this.max, this.minValue));
        this.maxValue = Math.min(this.max, Math.max(this.min, this.maxValue));
        if (this.minValue > this.maxValue) {
            [this.minValue, this.maxValue] = [this.maxValue, this.minValue]; // Swap if necessary
        }
    }

    formatNumber(num) {
        // Format number in Persian style
        return new Intl.NumberFormat('fa-IR').format(num);
    }

    updateInputs() {
        // Update input fields with formatted numbers
        this.minInput.value = this.formatNumber(this.minValue);
        this.maxInput.value = this.formatNumber(this.maxValue);
    }

    updateSlider() {
        // Calculate percentage positions
        const minPercent = (this.minValue - this.min) / (this.max - this.min) * 100;
        const maxPercent = (this.maxValue - this.min) / (this.max - this.min) * 100;

        // Update styles for range bar and thumbs
        this.range.style.left = `${Math.max(0, Math.min(100, minPercent))}%`;
        this.range.style.right = `${Math.max(0, Math.min(100, 100 - maxPercent))}%`;

        this.minThumb.style.left = `${Math.max(0, Math.min(100, minPercent))}%`;
        this.maxThumb.style.left = `${Math.max(0, Math.min(100, maxPercent))}%`;
    }

    getValueFromPosition(clientX) {
        // Convert mouse X position to slider value
        const rect = this.track.getBoundingClientRect();
        let position = (clientX - rect.left) / rect.width;
        position = Math.max(0, Math.min(1, position));
        return Math.round(this.min + position * (this.max - this.min));
    }

    handleMouseDown(e, type) {
        // Track which thumb is being dragged
        if (type === 'min') this.isMinDragging = true;
        if (type === 'max') this.isMaxDragging = true;
    }

    handleMouseMove(e) {
        // Handle dragging logic
        if (!this.isMinDragging && !this.isMaxDragging) return;

        const value = this.getValueFromPosition(e.clientX);

        if (this.isMinDragging) {
            this.minValue = Math.max(
                this.min,
                Math.min(value, this.maxValue - 100) // Prevent overlap
            );
        }
        if (this.isMaxDragging) {
            this.maxValue = Math.min(
                this.max,
                Math.max(value, this.minValue + 100) // Prevent overlap
            );
        }

        this.updateSlider();
        this.updateInputs();
    }

    handleMouseUp() {
        // Stop dragging
        this.isMinDragging = false;
        this.isMaxDragging = false;
    }

    init() {
        // Attach event listeners
        this.minThumb.addEventListener('mousedown', (e) => this.handleMouseDown(e, 'min'));
        this.maxThumb.addEventListener('mousedown', (e) => this.handleMouseDown(e, 'max'));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', () => this.handleMouseUp());

        // Initial render
        this.updateSlider();
        this.updateInputs();
    }
}

/**
 * COPY TEXT MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows users to copy input text to clipboard with a single click
 * - Supports both desktop and mobile text selection
 * - Provides user feedback after copy action
 */

// Select the input and button elements
const inputField = document.getElementById('inputField');
const copyButton = document.getElementById('copyButton');

// Ensure elements exist before proceeding
if (inputField && copyButton) {
    // Add click event listener to the copy button
    copyButton.addEventListener('click', () => {
        inputField.select(); // Highlight the text
        inputField.setSelectionRange(0, 99999); // Ensure compatibility with mobile

        document.execCommand('copy'); // Copy the text to clipboard

        alert('کپی شد!'); // User feedback (optional)
    });
}
/**
 * TOGGLE PASSWORD VISIBILITY MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Toggles password input field between 'text' and 'password'
 * - Improves user experience by letting users view or hide their password
 */

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId); // Select the password input field by ID
    if (input.type === "password") {
        input.type = "text"; // Show the password
    } else {
        input.type = "password"; // Hide the password
    }
}
/**
 * TABS MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows switching between different content sections using tabs
 * - Highlights the active tab with custom styles
 * - Supports both light and dark themes
 * - Ensures smooth content display by hiding inactive sections
 */

// Select all tabs and tab content elements
const tabs = document.querySelectorAll('[data-tabs-target]');
const tabContents = document.querySelectorAll('[role="tabpanel"]');

// Only proceed if tabs exist
if (tabs.length > 0 && tabContents.length > 0) {
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = document.querySelector(tab.dataset.tabsTarget); // Get the target content

            // Skip if target does not exist
            if (!target) return;

            // Remove active styles from all tabs
            tabs.forEach(t => {
                t.classList.remove('active', 'border-primary', 'text-primary', 'dark:border-primary-dark', 'dark:text-primary-dark');
                t.classList.add('border-transparent', 'hover:text-gray-600', 'hover:border-gray-300', 'dark:hover:text-gray-300');
            });

            // Apply active styles to the clicked tab
            tab.classList.add('active', 'border-primary', 'text-primary', 'dark:border-primary-dark', 'dark:text-primary-dark');
            tab.classList.remove('border-transparent', 'hover:text-gray-600', 'hover:border-gray-300', 'dark:hover:text-gray-300');

            // Hide all tab content sections
            tabContents.forEach(content => content.classList.add('hidden'));

            // Show the target content
            target.classList.remove('hidden');
        });
    });
}


/**
 * DISCOUNT CODE MODAL MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Displays a modal with discount code details (code, type, expiry, min purchase, group)
 * - Allows users to copy the discount code to clipboard
 * - Provides visual feedback after copying the code
 */

////////////////////////////////////////////////////////////////////////
// Show discount code modal
function showCodeModal(code, type, expiry, minPurchase, group) {
    // Update modal content with the provided discount code details
    document.getElementById('discountCode').textContent = code;
    document.getElementById('modalTitle').textContent = type;
    document.getElementById('discountType').textContent = type;
    document.getElementById('discountGroup').textContent = group;
    document.getElementById('discountExpiry').textContent = expiry;
    document.getElementById('discountMinPurchase').textContent = minPurchase;

    // Display the modal
    document.getElementById('discountCodeModal').classList.remove('hidden');
}

// Hide the discount code modal
function hideCodeModal() {
    // Add 'hidden' class to hide the modal
    document.getElementById('discountCodeModal').classList.add('hidden');
}

// Copy discount code
function copyCode() {
    const code = document.getElementById('discountCode').textContent; // Get the discount code text
    navigator.clipboard.writeText(code).then(() => {
        const copyButton = document.querySelector('#discountCodeModal button[onclick="copyCode()"]');
        const originalInnerHTML = copyButton.innerHTML;

        // Change button content to indicate the code was copied successfully
        copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>';

        // Restore the original button content after 2 seconds
        setTimeout(() => {
            copyButton.innerHTML = originalInnerHTML;
        }, 2000);
    });
}

/**
 * NOTIFICATION MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows switching between tabs
 * - Marks individual notifications as read
 * - Marks all notifications as read
 * - Deletes individual or all notifications
 */

////////////////////////////////////////////////////////////////////////
// Change active tab
function changeTab(tabId) {
    // Remove active class from all tabs
    document.querySelectorAll('[id$="-tab"]').forEach(tab => {
        tab.classList.remove('tab-active');
        tab.classList.add('bg-white', 'dark:bg-gray-700', 'border', 'border-gray-200', 'dark:border-gray-600');
    });

    // Add active class to the selected tab
    const activeTab = document.getElementById(`${tabId}-tab`);
    activeTab.classList.add('tab-active');
    activeTab.classList.remove('bg-white', 'dark:bg-gray-700', 'border', 'border-gray-200', 'dark:border-gray-600');

    // You can add the logic for filtering notifications based on the selected tab here
    console.log(`Tab ${tabId} selected`);
}

// Mark notification as read
function markAsRead(button) {
    const notification = button.closest('.border-b');
    if (notification) {
        notification.classList.remove('bg-blue-50', 'dark:bg-blue-900/20'); // Remove unread styles
    }
    button.textContent = 'خوانده شده'; // Update button text
    button.classList.remove('text-gray-500', 'dark:text-gray-400');
    button.classList.add('text-success', 'dark:text-success-dark'); // Change button color to indicate it's read
}

// Mark all notifications as read
function markAllAsRead() {
    // Remove unread styles from all notifications
    document.querySelectorAll('.bg-blue-50, .dark\\:bg-blue-900\\/20').forEach(el => {
        el.classList.remove('bg-blue-50', 'dark:bg-blue-900/20');
    });

    // Update all buttons to indicate they have been read
    document.querySelectorAll('[onclick="markAsRead(this)"]').forEach(button => {
        button.textContent = 'خوانده شده';
        button.classList.remove('text-gray-500', 'dark:text-gray-400');
        button.classList.add('text-success', 'dark:text-success-dark');
    });
}

// Delete a single notification
function deleteNotification(button) {
    const notification = button.closest('.border-b, .p-5:not(.border-b)');
    if (notification) {
        notification.remove(); // Remove the notification from the DOM
    }
}

// Delete all notifications
function deleteAllNotifications() {
    const notificationsContainer = document.querySelector('.border.rounded-xl.overflow-hidden');
    if (notificationsContainer) {
        // Clear all notifications and display a message indicating no notifications
        notificationsContainer.innerHTML = '<div class="p-8 text-center text-gray-500 dark:text-gray-400">هیچ اطلاعیه‌ای وجود ندارد</div>';
    }
}

/**
 * TRANSFER MONEY MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows selecting predefined amounts or entering a custom amount
 * - Calculates transaction fee and total amount
 * - Validates the entered amount
 * - Shows or hides error messages based on the amount entered
 * - Provides real-time search for the receiver
 */

document.addEventListener("DOMContentLoaded", function () {
    // Select all amount buttons and related elements
    const amountButtons = document.querySelectorAll(".amount-btn");
    const amountInput = document.getElementById("amount");
    const feeAmountElement = document.getElementById("fee-amount");
    const totalAmountElement = document.getElementById("total-amount");
    const amountErrors = document.getElementById("amount-errors");
    const receiverInput = document.getElementById("receiver");
    const receiverResult = document.getElementById("receiver-result");

    // Check if elements exist before proceeding
    if (amountButtons.length > 0 && amountInput) {
        amountButtons.forEach((btn) => {
            // Handle button click
            btn.addEventListener("click", function () {
                // Remove active class from all buttons
                amountButtons.forEach((b) => {
                    b.classList.remove(
                        "bg-primary/10",
                        "border-primary",
                        "text-primary",
                        "dark:bg-primary/20",
                        "dark:border-primary-dark",
                        "dark:text-primary-dark"
                    );
                });

                // Add active class to the selected button
                this.classList.add(
                    "bg-primary/10",
                    "border-primary",
                    "text-primary",
                    "dark:bg-primary/20",
                    "dark:border-primary-dark",
                    "dark:text-primary-dark"
                );

                // Set the amount in the input field
                amountInput.value = this.dataset.amount;

                // Calculate fee and total amount
                calculateFeeAndTotal();
            });
        });

        // Handle manual input in the amount field
        amountInput.addEventListener("input", function () {
            // Remove active class from all buttons if user enters amount manually
            amountButtons.forEach((b) => {
                b.classList.remove(
                    "bg-primary/10",
                    "border-primary",
                    "text-primary",
                    "dark:bg-primary/20",
                    "dark:border-primary-dark",
                    "dark:text-primary-dark"
                );
            });

            // Ensure only numeric values are entered
            this.value = this.value.replace(/[^0-9]/g, "");

            // Calculate fee and total amount
            calculateFeeAndTotal();
        });
    }

    // Function to calculate fee and total amount
    function calculateFeeAndTotal() {
        if (!amountInput || !feeAmountElement || !totalAmountElement || !amountErrors) return;

        const amount = parseInt(amountInput.value.replace(/,/g, "")) || 0;
        const feeAmount = Math.floor(amount * 0.005); // 0.5% fee
        const totalAmount = amount + feeAmount;

        // Show or hide error message
        if (amount < 50000 || amount > 10000000) {
            amountErrors.classList.remove("hidden");
        } else {
            amountErrors.classList.add("hidden");
        }

        // Display the amounts
        feeAmountElement.textContent = feeAmount.toLocaleString() + " تومان";
        totalAmountElement.textContent = totalAmount.toLocaleString() + " تومان";
    }

    // Search for receiver
    if (receiverInput && receiverResult) {
        receiverInput.addEventListener("input", function () {
            // Show or hide receiver results based on input length
            if (this.value.length > 3) {
                receiverResult.classList.remove("hidden");
            } else {
                receiverResult.classList.add("hidden");
            }
        });
    }
});

/**
 * MENU TOGGLE MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Allows toggling visibility of menu items
 * - Rotates the arrow icon when the menu is toggled
 * - Closes the menu when clicking outside
 */

// Toggle Menu Function
function toggleMenu(menuId, arrowIconId) {
    const menu = document.getElementById(menuId); // Get the menu element
    const icon = document.getElementById(arrowIconId); // Get the arrow icon element

    menu.classList.toggle('hidden'); // Toggle visibility of the menu
    icon.classList.toggle('rotate-180'); // Rotate the arrow icon when menu is toggled
}

// Close Menu When Click Outside
document.addEventListener('click', function(event) {
    // Close all menus if the click is outside any menu or toggle button
    if (!event.target.closest('[onclick*="toggleMenu"]')) {
        document.querySelectorAll('[id$="-menu"]').forEach(menu => {
            menu.classList.add('hidden'); // Hide the menu
        });
        document.querySelectorAll('[id$="-arrow-icon"]').forEach(icon => {
            icon.classList.remove('rotate-180'); // Reset the arrow icon rotation
        });
    }
});



/**
 * DROPDOWN MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Toggles the visibility of the user dropdown menu
 * - Rotates the dropdown icon when the menu is displayed
 * - Closes the dropdown if clicked outside of the menu
 */

// Toggle User Dropdown
function toggleUserDropdown() {
    const menu = document.getElementById("user-dropdown-menu"); // Get the dropdown menu
    const icon = document.getElementById("user-dropdown-icon"); // Get the dropdown icon

    // Toggle the menu display (show or hide)
    if (menu) {
        menu.style.display = (menu.style.display === "block") ? "none" : "block";
    }

    // Toggle icon rotation (flip the icon when the menu is open)
    if (icon) {
        icon.classList.toggle("rotate-180");
    }
}

// Close dropdown if clicked outside
document.addEventListener("click", function (event) {
    const dropdown = document.getElementById("user-dropdown"); // Get the dropdown container
    const menu = document.getElementById("user-dropdown-menu"); // Get the dropdown menu
    const icon = document.getElementById("user-dropdown-icon"); // Get the dropdown icon

    // Ensure dropdown, menu, and icon exist before proceeding
    if (dropdown && menu && icon) {
        // If click is outside the dropdown, hide the menu and reset the icon
        if (!dropdown.contains(event.target)) {
            menu.style.display = "none"; // Hide the menu
            icon.classList.remove("rotate-180"); // Reset icon rotation
        }
    }
});


/**
 * COMPONENT CODE TOGGLER & COPIER MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Toggles visibility of a code block when clicking the toggle button
 * - Copies code block content to clipboard with success/error handling
 * - Provides user feedback with alert messages
 */

// Toggle code
function toggleComponentCode(btn) {
    const codeBlock = btn.nextElementSibling;
    if (codeBlock) codeBlock.classList.toggle('hidden');
}

// Copy code
function copyComponentCode(btn) {
    const block = btn.closest('.code-block');
    const codeBlock = block ? block.querySelector('code') : null;

    if (!codeBlock) {
        alert('کدی برای کپی پیدا نشد!');
        return;
    }

    navigator.clipboard.writeText(codeBlock.textContent.trim())
        .then(() => alert('کد با موفقیت کپی شد!'))
        .catch(() => alert('کپی کردن کد با خطا مواجه شد!'));
}


/**
 * LIVE SEARCH MODULE
 * Designed by Amir Rezaie
 * Features:
 * - Live search with debounce to prevent unnecessary requests
 * - Displays results based on product name or category
 * - Shows a loading indicator while searching
 * - Handles focus/blur and outside clicks to close the results list
 * - Allows selecting an item and inserting it into the input
 * - Supports pressing Enter key for manual search trigger
 */


// Safe function to execute code only when elements exist
function initializeLiveSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    // If the required elements are not present, the code will not be executed
    if (!searchInput || !searchResults) {
        return;
    }

    let debounceTimer;

    // Sample product data
    const products = [
        { id: 1, name: "لپ تاپ ایسوس مدل ROG", category: "لپ تاپ و کامپیوتر" },
        { id: 2, name: "گوشی سامسونگ گلکسی S23", category: "موبایل و تبلت" },
        { id: 3, name: "هدفون بی سیم سونی", category: "لوازم جانبی" },
        { id: 4, name: "ماوس گیمینگ رزر", category: "لوازم جانبی" },
        { id: 5, name: "تلویزیون ال جی 55 اینچ", category: "صوتی و تصویری" },
        { id: 6, name: "کتاب صوتی موفقیت در کسب و کار", category: "کتاب و رسانه" },
        { id: 7, name: "کفش ورزشی نایک", category: "پوشاک و ورزش" },
        { id: 8, name: "دستگاه غذاساز فیلیپس", category: "لوازم خانگی" },
        { id: 9, name: "دوربین کانن EOS R5", category: "عکاسی" },
        { id: 10, name: "کنسول بازی پلی استیشن 5", category: "بازی و سرگرمی" }
    ];

    // Search function
    function performSearch(searchTerm) {
        if (searchTerm.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        // Show loading status
        searchResults.innerHTML = `
                    <div class="p-4 text-center text-gray-600 dark:text-gray-300">
                        <div class="loading">در حال جستجو</div>
                    </div>
                `;
        searchResults.classList.remove('hidden');

        // Simulate server response delay
        setTimeout(() => {
            const results = products.filter(product =>
                product.name.includes(searchTerm) ||
                product.category.includes(searchTerm)
            );

            displayResults(results);
        }, 600);
    }

    // Show results
    function displayResults(results) {
        if (results.length === 0) {
            searchResults.innerHTML = `
                        <div class="p-4 text-center text-gray-600 dark:text-gray-300">
                            نتیجه‌ای یافت نشد
                        </div>
                    `;
            return;
        }

        searchResults.innerHTML = '';
        results.forEach(product => {
            const resultItem = document.createElement('div');
            resultItem.className = 'p-4 border-b border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors';
            resultItem.innerHTML = `
                        <a href='shop.html'>
                            <div class="font-semibold text-gray-800 dark:text-white">${product.name}</div>
                            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">${product.category}</div>
                        </a>
                    `;
            resultItem.addEventListener('click', () => {
                searchInput.value = product.name;
                searchResults.classList.add('hidden');
            });
            searchResults.appendChild(resultItem);
        });
    }

    // Event management for delayed live search (debounce)
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const searchTerm = this.value.trim();

        if (searchTerm) {
            debounceTimer = setTimeout(() => {
                performSearch(searchTerm);
            }, 300);
        } else {
            searchResults.classList.add('hidden');
        }
    });

    // Focus and blur management
    searchInput.addEventListener('focus', function() {
        const searchTerm = this.value.trim();
        if (searchTerm.length >= 2) {
            performSearch(searchTerm);
        }
    });

    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    // Ability to search with the Enter button
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchTerm = this.value.trim();
            if (searchTerm) {
                alert(`جستجو برای: ${searchTerm} (این قسمت به صفحه نتایج جستجو هدایت می‌کند)`);
            }
        }
    });
}

// Execute the function when the DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeLiveSearch);
} else {
    initializeLiveSearch();
}

// You can also put the function in global scope so that it can be accessed from other pages
window.initializeLiveSearch = initializeLiveSearch;


/**
 * COUNTDOWN TIMER MODULE
 * Designed by [Your Name]
 * Features:
 * - Countdown timer with days, hours, minutes, and seconds
 * - Dark mode support with toggle functionality
 * - Responsive design with Tailwind CSS
 * - Automatic update every second
 * - Compatible with existing countdown div structure
 */

// Function to add zero to numbers less than 10
function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

// Main function for timer display
function showCountdown(element) {
    var currentDate = new Date();
    var fieldDate = element.getAttribute('data-date').split('-');
    var fieldTime = [0, 0];

    if(element.getAttribute('data-time') != undefined) {
        fieldTime = element.getAttribute('data-time').split(':');
    }

    var futureDate = new Date(fieldDate[0], fieldDate[1]-1, fieldDate[2], fieldTime[0], fieldTime[1]);
    var seconds = futureDate.getTime() / 1000 - currentDate.getTime() / 1000;

    if(seconds <= 0 || isNaN(seconds)){
        element.style.display = 'none';
        return;
    }

    var days = Math.floor(seconds/86400);
    seconds = seconds % 86400;

    var hours = Math.floor(seconds/3600);
    seconds = seconds % 3600;

    var minutes = Math.floor(seconds/60);
    seconds = Math.floor(seconds % 60);

    var html = "";

    if(days != 0){
        html += "<div class='countdown-container space-x-1 flex items-center text-center mx-1'>";
        html += "<span class='countdown-value block bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white text-xs font-bold size-6 flex items-center justify-center rounded-lg mb-1'>" + pad(days) + "</span>";
        html += "<span class='countdown-heading block text-xs font-bold text-gray-800 dark:text-white'>/</span>";
        html += "</div>";
    }

    html += "<div class='countdown-container space-x-1 flex items-center text-center mx-1'>";
    html += "<span class='countdown-value block bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white text-xs font-bold size-6 flex items-center justify-center rounded-lg mb-1'>" + pad(hours) + "</span>";
    html += "<span class='countdown-heading block text-xs font-bold text-gray-800 dark:text-white'>:</span>";
    html += "</div>";

    html += "<div class='countdown-container space-x-1 flex items-center text-center mx-1'>";
    html += "<span class='countdown-value block bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white text-xs font-bold size-6 flex items-center justify-center rounded-lg mb-1'>" + pad(minutes) + "</span>";
    html += "<span class='countdown-heading block text-xs font-bold text-gray-800 dark:text-white'>:</span>";
    html += "</div>";

    html += "<div class='countdown-container space-x-1 flex items-center text-center mx-1'>";
    html += "<span class='countdown-value block bg-primary dark:bg-primary-600 text-white text-xs font-bold size-6 flex items-center justify-center rounded-lg mb-1'>" + pad(seconds) + "</span>";
    html += "</div>";

    element.innerHTML = html;
    element.style.display = 'flex';
    element.classList.add('justify-start', 'items-center');
}

// Function to start the timer
function initCountdown() {
    var countdownElements = document.querySelectorAll('.countdown');

    if(countdownElements.length > 0) {
        countdownElements.forEach(function(element) {
            showCountdown(element);
            setInterval(function() {
                showCountdown(element);
            }, 1000);
        });
    }
}


// Launch after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCountdown();
});


/**
 * SCROLL TO TOP FUNCTION
 * Description: Smoothly scrolls the page to the top of the window.
 */
function scrollToTop(e) {
    e.preventDefault();
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}


/**
 * COLOR SELECTOR INITIALIZER
 * Description: Updates the displayed selected color when a radio button changes.
 * Safety: Runs safely even if elements are missing on the page.
 * Default Behavior: On page load, sets the displayed color to the currently checked option.
 */
function initColorSelector() {
    const radios = document.querySelectorAll('input[name="color"]');
    const output = document.getElementById('selectedColor');

    // Exit if elements do not exist (safe mode)
    if (!radios.length || !output) return;

    // Set initial color on page load
    const checkedRadio = document.querySelector('input[name="color"]:checked');
    if (checkedRadio) {
        output.textContent = checkedRadio.value;
    }

    // Update color text when user selects a new option
    radios.forEach(radio => {
        radio.addEventListener('change', () => {
            output.textContent = radio.value;
        });
    });
}

// Auto-run when the page is fully loaded
document.addEventListener('DOMContentLoaded', initColorSelector);


/**
 * VERTICAL SLIDER INITIALIZER
 * Description: Creates an automatic vertical sliding animation that moves upward.
 * Safety: Runs safely even if the slider element does not exist on the page.
 * Default Behavior: Starts sliding from the first slide and loops infinitely.
 */
function initVerticalSlider() {
    const slider = document.getElementById("verticalSlider");
    const slideHeight = 40; // Height of each slide (px)
    const interval = 2500; // Time between slides
    const transitionSpeed = 500; // Slide animation duration (ms)

    // Exit if slider does not exist (safe mode)
    if (!slider) return;

    // Detect number of slides dynamically
    const slidesCount = slider.children.length;
    let current = 0;

    // Auto sliding logic
    setInterval(() => {
        current++;

        // Move slider upward with smooth animation
        slider.style.transform = `translateY(-${current * slideHeight}px)`;
        slider.style.transition = `transform ${transitionSpeed}ms ease-in-out`;

        // Reset when reaching the end
        if (current === slidesCount) {
            setTimeout(() => {
                slider.style.transition = "none"; // Disable animation for reset
                slider.style.transform = "translateY(0)";
                current = 0; // Restart index
            }, transitionSpeed + 100); // Reset after animation ends
        }
    }, interval);
}

// Auto-run on page load
document.addEventListener("DOMContentLoaded", initVerticalSlider);


/**
 * TAB SCROLL & ACTIVE HIGHLIGHT MODULE
 * Designed by Amir Rezaie
 *
 * Features:
 * - Automatically activates the correct tab while scrolling
 * - Scrolls tab bar horizontally to keep the active tab centered
 * - Smooth scrolling to sections when clicking tabs
 * - Fully responsive and optimized for mobile
 */

document.addEventListener("DOMContentLoaded", function () {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabSections = document.querySelectorAll('.tab-section');
    const tabContainer = document.getElementById('tabContainer');

    let currentActiveTab = 0;
    let isScrolling = false;

    if (!tabButtons.length || !tabSections.length || !tabContainer) {
        return;
    }

    // Activate the first tab
    activateTab(0);

    // Click on a tab
    tabButtons.forEach((tab, index) => {
        tab.addEventListener('click', () => {
            if (!tabSections[index]) return;

            isScrolling = true;
            activateTab(index);

            tabSections[index].scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            setTimeout(() => {
                isScrolling = false;
            }, 1000);
        });
    });

    // Detect scroll and update active tab
    window.addEventListener('scroll', () => {
        if (isScrolling) return;

        let activeIndex = -1;
        const scrollPosition = window.scrollY + 120;

        tabSections.forEach((section, index) => {
            const rect = section.getBoundingClientRect();
            const sectionTop = rect.top + window.scrollY;
            const sectionBottom = sectionTop + rect.height;

            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeIndex = index;
            }
        });

        if (activeIndex !== -1 && currentActiveTab !== activeIndex) {
            activateTab(activeIndex);
        }
    });

    // Activate a tab
    function activateTab(index) {
        if (!tabButtons[index]) return;

        // Reset all buttons
        tabButtons.forEach(btn => {
            btn.classList.remove(
                'active', 'bg-primary', 'text-white',
                'dark:bg-primary', 'dark:text-white', 'font-bold'
            );
            btn.classList.add(
                'bg-blue-100', 'text-primary-800',
                'dark:bg-blue-800/30', 'dark:text-gray-200'
            );
        });

        // Apply active styles
        const activeBtn = tabButtons[index];
        activeBtn.classList.add(
            'active', 'bg-primary', 'text-white',
            'dark:bg-primary', 'dark:text-white', 'font-bold'
        );
        activeBtn.classList.remove(
            'bg-blue-100', 'text-primary-800',
            'dark:bg-blue-800/30', 'dark:text-gray-200'
        );

        currentActiveTab = index;
        scrollTabIntoView(index);
    }

    // Center active tab inside horizontal scroll container
    function scrollTabIntoView(index) {
        if (!tabContainer || !tabButtons[index]) return;

        const tab = tabButtons[index];
        const containerWidth = tabContainer.offsetWidth;
        const tabLeft = tab.offsetLeft;
        const tabWidth = tab.offsetWidth;

        const scrollPos = tabLeft - (containerWidth / 2) + (tabWidth / 2);

        tabContainer.scrollTo({
            left: Math.max(0, scrollPos),
            behavior: 'smooth'
        });
    }
});

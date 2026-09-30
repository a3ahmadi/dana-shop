/**
 * StoryPlayer - A customizable story viewer component
 * @version 2.0.0
 * @class
 */

class StoryPlayer {
    /**
     * Constructor to initialize the story player.
     * @param {string} containerId - The ID of the container element.
     * @param {Array} stories - An array of story objects.
     */
    constructor(containerId, stories) {
        this.container = document.getElementById(containerId);
        this.stories = stories;
        this.currentStoryIndex = 0;
        this.timer = null;
        this.videoDuration = null;
        this.isPaused = false;
        this.touchStartX = 0;
        this.touchEndX = 0;

        this.init();
    }

    /**
     * Initialize the story player by rendering stories
     */
    init() {
        this.renderStories();
    }

    /**
     * Render the stories in the container.
     */
    renderStories() {
        this.container.innerHTML = this.stories.map((story, index) => `
            <div class="story" data-index="${index}">
                <div class="story-avatar">
                    <img src="${story.avatar}" alt="${story.user}" onerror="this.src='https://picsum.photos/70'">
                </div>
                <div class="story-username dark:!text-white">${story.user}</div>
            </div>
        `).join('');

        document.querySelectorAll('.story').forEach(story => {
            story.addEventListener('click', () => {
                this.currentStoryIndex = parseInt(story.dataset.index);
                this.openStory();
            });
        });
    }

    /**
     * Open the selected story.
     */
    openStory() {
        this.createModal();
        this.loadStory();
    }

    /**
     * Create the modal for displaying stories.
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'story-modal';
        this.modal.innerHTML = `
            <div class="progress-container">
                <div class="progress-fill"></div>
            </div>
            <div class="story-content">
                <button class="close-button">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
                    </svg>
                </button>
                <button class="nav-button prev-button">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                    </svg>
                </button>
                <div class="media-container">
                    <img class="story-media" alt="Story">
                    <video class="video-media"></video>
                    <a href="#" class="story-link" target="_blank" style="display: none;">مشاهده لینک</a>
                </div>
                <button class="nav-button next-button">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
                    </svg>
                </button>
            </div>
        `;
        document.body.appendChild(this.modal);
        this.setupModalEventListeners();
    }

    /**
     * Load the current story into the modal.
     */
    loadStory() {
        const story = this.stories[this.currentStoryIndex];
        this.modal.style.display = 'block';

        // Display the link if available
        const storyLink = this.modal.querySelector('.story-link');
        storyLink.style.display = story.link ? 'block' : 'none';
        storyLink.href = story.link || '#';

        if (story.type === 'video') {
            this.setupVideo(story);
        } else {
            this.setupImage(story);
        }

        // Mark the story as viewed
        document.querySelectorAll('.story-avatar')[this.currentStoryIndex].classList.add('viewed');
    }

    /**
     * Setup the video story.
     * @param {Object} story - The story object containing video URL.
     */
    setupVideo(story) {
        const videoMedia = this.modal.querySelector('.video-media');
        const imageMedia = this.modal.querySelector('.story-media');
        imageMedia.style.display = 'none';
        videoMedia.style.display = 'block';
        videoMedia.src = story.url;

        videoMedia.onloadedmetadata = () => {
            this.videoDuration = videoMedia.duration * 1000;
            this.resetProgressBar();
            this.startVideoProgress();
        };

        videoMedia.onended = () => {
            this.nextStory();
        };

        videoMedia.play();
    }

    /**
     * Setup the image story.
     * @param {Object} story - The story object containing image URL.
     */
    setupImage(story) {
        const videoMedia = this.modal.querySelector('.video-media');
        const imageMedia = this.modal.querySelector('.story-media');
        videoMedia.style.display = 'none';
        imageMedia.style.display = 'block';
        imageMedia.src = story.url;
        this.resetProgressBar();
        this.startTimer(story.duration);
    }

    /**
     * Start the timer for image stories.
     * @param {number} duration - The duration of the story in milliseconds.
     */
    startTimer(duration) {
        const progressFill = this.modal.querySelector('.progress-fill');
        progressFill.style.transition = `width ${duration}ms linear`;
        progressFill.style.width = '100%';

        this.timer = setTimeout(() => {
            if (!this.isPaused) this.nextStory();
        }, duration);
    }

    /**
     * Start the progress bar for video stories.
     */
    startVideoProgress() {
        const progressFill = this.modal.querySelector('.progress-fill');
        progressFill.style.transition = 'none';
        progressFill.style.width = '0%';

        setTimeout(() => {
            progressFill.style.transition = `width ${this.videoDuration}ms linear`;
            progressFill.style.width = '100%';
        }, 50);
    }


    /**
     * Go to the next story.
     */
    nextStory() {
        if (this.currentStoryIndex < this.stories.length - 1) {
            this.currentStoryIndex++;
            this.resetMedia();
            this.loadStory();
        } else {
            this.closeStory();
        }
    }

    /**
     * Go to the previous story.
     */
    prevStory() {
        if (this.currentStoryIndex > 0) {
            this.currentStoryIndex--;
            this.resetMedia();
            this.loadStory();
        }
    }

    /**
     * Reset the media elements in the modal.
     */
    resetMedia() {
        const progressFill = this.modal.querySelector('.progress-fill');
        const videoMedia = this.modal.querySelector('.video-media');
        progressFill.style.width = '0%';
        videoMedia.pause();
        videoMedia.currentTime = 0;
        clearTimeout(this.timer);
        this.isPaused = false;
        videoMedia.ontimeupdate = null;
    }

    /**
     * Reset the progress bar.
     */
    resetProgressBar() {
        const progressFill = this.modal.querySelector('.progress-fill');
        progressFill.style.transition = 'none';
        progressFill.style.width = '0%';
        void progressFill.offsetWidth; // Force reflow
    }

    /**
     * Close the story modal.
     */
    closeStory() {
        this.resetMedia();
        this.modal.remove();
    }

    /**
     * Setup event listeners for the modal.
     */
    setupModalEventListeners() {
        const closeBtn = this.modal.querySelector('.close-button');
        const prevBtn = this.modal.querySelector('.prev-button');
        const nextBtn = this.modal.querySelector('.next-button');
        const mediaContainer = this.modal.querySelector('.media-container');

        closeBtn.addEventListener('click', () => this.closeStory());
        prevBtn.addEventListener('click', () => this.prevStory());
        nextBtn.addEventListener('click', () => this.nextStory());

        mediaContainer.addEventListener('click', () => this.togglePause());

        // Add touch swipe functionality
        mediaContainer.addEventListener('touchstart', (e) => {
            this.touchStartX = e.changedTouches[0].clientX;
        });

        mediaContainer.addEventListener('touchend', (e) => {
            this.touchEndX = e.changedTouches[0].clientX;
            this.handleSwipe();
        });
    }
    /**
     * Handle swipe gestures to navigate stories.
     */
    handleSwipe() {
        const swipeThreshold = 50; // Minimum distance for a swipe gesture
        const swipeDistance = this.touchEndX - this.touchStartX;

        if (swipeDistance > swipeThreshold) {
            this.prevStory();
        } else if (swipeDistance < -swipeThreshold) {
            this.nextStory();
        }
    }

    /**
     * Toggle the pause state of the story.
     */
    togglePause() {
        this.isPaused = !this.isPaused;
        const videoMedia = this.modal.querySelector('.video-media');
        if (this.stories[this.currentStoryIndex].type === 'video') {
            this.isPaused ? videoMedia.pause() : videoMedia.play();
        }
        this.handleProgressBar();
    }

    /**
     * Handle the progress bar based on the pause state.
     */
    handleProgressBar() {
        if (this.isPaused) {
            clearTimeout(this.timer);
            const progressFill = this.modal.querySelector('.progress-fill');
            progressFill.style.transition = 'none';
            progressFill.style.width = getComputedStyle(progressFill).width;
        } else {
            if (this.stories[this.currentStoryIndex].type === 'video') {
                this.startVideoProgress();
            } else {
                this.startTimer(this.calculateRemainingTime());
            }
        }
    }

    /**
     * Calculate the remaining time for the current story.
     * @return {number} - The remaining time in milliseconds.
     */
    calculateRemainingTime() {
        const story = this.stories[this.currentStoryIndex];
        const progressFill = this.modal.querySelector('.progress-fill');
        const currentWidth = parseFloat(progressFill.style.width);
        const totalDuration = story.type === 'video' ? this.videoDuration : story.duration;
        return (1 - currentWidth / 100) * totalDuration;
    }
}

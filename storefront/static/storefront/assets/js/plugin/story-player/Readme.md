```markdown
# StoryPlayer Component Documentation

📖 A customizable story viewer component for displaying image/video stories with interactive controls

## ✨ Features
- Image & video story support
- Auto-play video stories
- Interactive progress bar
- Gesture controls (swipe navigation)
- Keyboard navigation support
- Customizable story duration
- Pause/Resume functionality
- Responsive design
- Touch device optimized
- Event-driven architecture
- Link support in stories

## 📦 Installation
```html
<!-- CSS -->
<link rel="stylesheet" href="path/to/storyplayer.css">

<!-- JavaScript -->
<script src="path/to/storyplayer.js"></script>
```

## 🚀 Basic Usage
```javascript
// Initialize StoryPlayer
const stories = [
  {
    type: 'image',
    user: 'John Doe',
    avatar: 'user1.jpg',
    url: 'story1.jpg',
    duration: 5000,
    link: 'https://example.com'
  },
  {
    type: 'video',
    user: 'Jane Smith',
    avatar: 'user2.jpg',
    url: 'story2.mp4',
    duration: 10000
  }
];

const storyPlayer = new StoryPlayer('story-container', stories);
```

## 🛠️ Configuration Options
| Property    | Type   | Default | Description                      |
|-------------|--------|---------|----------------------------------|
| containerId | string | -       | Target container element ID      |
| stories     | array  | []      | Array of story objects           |

## 📖 Story Object Structure
```javascript
{
  type: 'image' || 'video',  // Required
  user: 'String',            // Display name
  avatar: 'URL',             // User avatar
  url: 'URL',                // Media URL
  duration: Number,          // Display time (ms)
  link: 'URL'                // Optional link
}
```

## 🎮 Public Methods
```javascript
// Open story viewer
storyPlayer.openStory();

// Navigate to next story
storyPlayer.nextStory();

// Navigate to previous story
storyPlayer.prevStory();

// Toggle pause state
storyPlayer.togglePause();

// Close story viewer
storyPlayer.closeStory();
```

## 🌐 Browser Support
| Browser       | Version |
|---------------|---------|
| Chrome        | 58+     |
| Firefox       | 55+     |
| Safari        | 11+     |
| Edge          | 16+     |
| Mobile Safari | 11+     |
| Chrome Android| 81+     |

## ⚙️ Technical Specs
- Video autoplay on story open
- Automatic video duration detection
- Progress bar sync with media playback
- Memory efficient media handling
- Touch event handling
- Clean resource management

## 📜 License
MIT License - See [LICENSE](LICENSE) for details

---

**Developer**: Amir Rezaie  
**Creation Date**: October 2023  


```

This documentation provides:
1. Component overview
2. Installation instructions
3. Configuration options
4. Usage examples
5. Event handling
6. Customization guide
7. Browser support info
8. Technical specifications
9. License information
10. Developer credits

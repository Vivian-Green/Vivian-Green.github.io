document.addEventListener("DOMContentLoaded", function () {
    const postList = document.getElementById('post-list');
    const thumbnailGrid = document.getElementById('thumbnail-grid');
    const rightPanel = document.querySelector('#right-panel'); // Get the right panel element

    // Function to check orientation and handle panel visibility
    function handleOrientation() {
        if (window.innerWidth < window.innerHeight) {
            // Portrait mode - hide thumbnail panel
            rightPanel.style.display = 'none';
            leftPanelInner = document.querySelector('#left-panel-inner');
            leftPanelInner.style.margin = '0 20px';
        } else {
            // Landscape mode - show thumbnail panel
            rightPanel.style.display = 'block';
            leftPanelInner = document.querySelector('#left-panel-inner');
            leftPanelInner.style.margin = '0 120px';
        }
    }

    // Initial check
    handleOrientation();

    // Add resize listener
    window.addEventListener('resize', handleOrientation);

    // Load recent posts first, then older posts
    loadJSON('https://vivian-green.github.io/recentPosts.json')
        .then(data => {
            renderPosts(data);
            // After recent posts load, fetch older posts
            return loadJSON('https://vivian-green.github.io/olderPosts.json');
        })
        .then(data => {
            renderPosts(data);
        })
        .catch(error => {
            console.error("Error loading posts:", error);
        });

    /**
     * Fetches and parses a JSON file from GitHub
     * @param {string} url - Raw GitHub URL of the JSON file
     * @returns {Promise<Array>} - Parsed JSON data
     */
    async function loadJSON(url) {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load ${url} (status: ${response.status})`);
        }
        return await response.json();
    }

    function renderPosts(posts) {
        if (!posts || !posts.length) return;

        posts.forEach(post => {
            // Create post preview
            const postPreview = document.createElement('div');
            postPreview.classList.add('post-preview');
            postPreview.innerHTML = `
                <p class="timestamp">${formatDateFromFilename(post.filename)}</p>
                <div class="post-content">${markdownToHTML(post.content)}</div>
            `;
            postList.appendChild(postPreview);

            // Create thumbnail if available
            if (post.thumbnail) {
                const thumbnail = document.createElement('div');
                thumbnail.classList.add('thumbnail');
                thumbnail.innerHTML = `
                    <p class="date">${formatDateFromFilename(post.filename)}</p>
                    <img src="${post.thumbnail}" alt="${post.title}" class="thumbnail-image">
                    <div class="thumbnail-overlay">
                        <span class="title">${post.title}</span>
                    </div>
                `;
                thumbnailGrid.appendChild(thumbnail);
            }
        });
    }

    // Check if marked is available
    if (typeof marked.marked !== 'function') {
        console.log(marked);
        console.log(marked.marked);
        console.error('marked is not available');
        return;
    }

    // Function to convert markdown to HTML using marked
    function markdownToHTML(markdown) {
        // Configure marked.js options for better code rendering
        marked.marked.setOptions({
            highlight: function(code, lang) {
                if (lang) {
                    return `<pre><code class="language-${lang}">${code}</code></pre>`;
                }
                return `<pre><code>${code}</code></pre>`;
            },
            langPrefix: 'language-',
            gfm: true,
            breaks: true
        });

        let html = marked.marked(markdown);
        const youtubeLinkRegex = /<a href="(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})".*?<\/a>/g;

        html = html.replace(youtubeLinkRegex, (match, videoId) => {
            return `<div style="margin: 10px 0; padding-left: 80px">
                        <iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}" 
                                frameborder="0" allowfullscreen></iframe>
                    </div>`;
        });

        return html;
    }

    // Function to format date from filename
    function formatDateFromFilename(filename) {
        const datePart = filename.slice(0, 12);
        const year = datePart.slice(0, 4);
        const month = datePart.slice(4, 6);
        const day = datePart.slice(6, 8);
        return `${month}/${day}/${year}`;
    }
});

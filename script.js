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
    window.addEventListener('hashchange', handleHashScroll);

    function showErrorMessage(message = "Posts couldn't be loaded. Please refresh or try again later.") {
        const container = document.getElementById('posts-container') || document.body;
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.innerHTML = `
            <p>⚠️ ${message}</p>
            <button onclick="window.location.reload()">Retry</button>
        `;
        container.prepend(errorElement);  // todo: ADD CSS FOR THIS ERROR- THIS RETRY BUTTON IS FUCKIN MIKE WAZOWSKI'D
    }

    // JSONP loader function
    function loadJSONP(url, callbackName) {
        return new Promise((resolve, reject) => {
            window[callbackName] = (data) => {
                delete window[callbackName];
                resolve(data);
            };
            
            const script = document.createElement('script');
            script.src = `${url}?callback=${callbackName}`;
            script.onerror = () => {
                delete window[callbackName];
                reject(new Error(`Failed to load ${url}`));
            };
            document.body.appendChild(script);
        });
    }

    // Main load function with JSONP fallback
    async function loadPosts() {
        try {
            // First try to load via JSONP
            const recent = await loadJSONP(
                'https://vivian-green.github.io/recentPosts.js',
                'handleRecentPosts'
            );
            
            const older = await loadJSONP(
                'https://vivian-green.github.io/olderPosts.js',
                'handleOlderPosts'
            );
            
            renderPosts(recent);
            renderPosts(older);
            
            // After posts are loaded, check for hash
            handleHashScroll();
            
        } catch (error) {
            console.error("JSONP failed, trying local fallback:", error);
            try {
                // Fallback to local files
                const localRecent = await fetch('/recentPosts.json').then(r => r.json());
                renderPosts(localRecent);
                handleHashScroll();
            } catch (e) {
                showErrorMessage();
            }
        }
    }

    function renderPosts(posts) {
        if (!posts || !posts.length) return;

        posts.forEach(post => {
            // Create a slug from the filename (or title) for the ID
            const postId = post.filename.replace(/\.md$/, '').replace(/[^a-z0-9]/gi, '-').toLowerCase();
            
            // Create post preview
            const postPreview = document.createElement('div');
            postPreview.classList.add('post-preview');
            postPreview.id = `post-${postId}`;  // Add ID here
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
                
                // Add click event to scroll to the relevant post
                thumbnail.addEventListener('click', () => {
                    const postElement = document.getElementById(`post-${postId}`);
                    if (postElement) {
                        postElement.scrollIntoView({ behavior: 'smooth' });
                        
                        // Update URL hash without triggering hashchange
                        const currentHash = window.location.hash.substring(1);
                        if (currentHash !== `post-${postId}`) {
                            history.replaceState(null, null, `#post-${postId}`);
                        }
                    }
                });
                
                // Add cursor pointer to indicate it's clickable
                thumbnail.style.cursor = 'pointer';
                
                thumbnailGrid.appendChild(thumbnail);
            }

            document.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        });
    }

    function handleHashScroll() {
        if (window.location.hash) {
            const postId = window.location.hash.substring(1); // Remove the #
            const element = document.getElementById(postId);
            if (element) {
                // Small timeout to ensure posts are loaded
                setTimeout(() => {
                    element.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
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
        marked.marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {
                        console.error('Highlight.js error:', err);
                    }
                }
                return hljs.highlightAuto(code).value;
            }
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

    loadPosts();
});

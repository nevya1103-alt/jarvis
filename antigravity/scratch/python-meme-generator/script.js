document.addEventListener('DOMContentLoaded', () => {
    const memeImage = document.getElementById('meme-image');
    const loadingState = document.getElementById('loading-state');
    const displayTopText = document.getElementById('display-top-text');
    const displayBottomText = document.getElementById('display-bottom-text');
    const topTextInput = document.getElementById('top-text-input');
    const bottomTextInput = document.getElementById('bottom-text-input');
    const randomBtn = document.getElementById('random-btn');
    const downloadBtn = document.getElementById('download-btn');
    const templateGallery = document.getElementById('template-gallery');
    const memeContainer = document.getElementById('meme-container');

    let memes = [];

    // Fetch memes from backend API
    async function fetchMemes() {
        try {
            const response = await fetch('/api/memes');
            const data = await response.json();
            
            if (data.success) {
                memes = data.memes;
                renderGallery();
                setRandomMeme();
            } else {
                loadingState.textContent = 'Failed to load templates: ' + data.error;
            }
        } catch (error) {
            console.error('Error fetching memes:', error);
            loadingState.textContent = 'Error connecting to server.';
        }
    }

    // Display a specific meme template
    function setMemeTemplate(url) {
        loadingState.style.display = 'none';
        memeImage.style.display = 'block';
        
        // Use a proxy or set crossOrigin to anonymous if possible to help html2canvas
        // But Imgflip API returns URLs that generally allow CORS
        memeImage.crossOrigin = "anonymous";
        memeImage.src = url;
    }

    // Choose a random meme template
    function setRandomMeme() {
        if (memes.length === 0) return;
        const currentMemeIndex = Math.floor(Math.random() * memes.length);
        setMemeTemplate(memes[currentMemeIndex].url);
    }

    // Render the gallery of popular templates
    function renderGallery() {
        templateGallery.innerHTML = '';
        // Only show first 24 templates to keep it clean
        const displayMemes = memes.slice(0, 24);
        
        displayMemes.forEach(meme => {
            const item = document.createElement('div');
            item.className = 'gallery-item';
            
            const img = document.createElement('img');
            img.src = meme.url;
            img.alt = meme.name;
            img.loading = "lazy";
            
            item.appendChild(img);
            
            item.addEventListener('click', () => {
                setMemeTemplate(meme.url);
                // Scroll up smoothly
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
            
            templateGallery.appendChild(item);
        });
    }

    // Event Listeners for Text Input
    topTextInput.addEventListener('input', (e) => {
        displayTopText.textContent = e.target.value;
    });

    bottomTextInput.addEventListener('input', (e) => {
        displayBottomText.textContent = e.target.value;
    });

    // Random Button
    randomBtn.addEventListener('click', setRandomMeme);

    // Download Button using html2canvas
    downloadBtn.addEventListener('click', () => {
        downloadBtn.textContent = 'Generating...';
        downloadBtn.disabled = true;
        
        setTimeout(() => {
            html2canvas(memeContainer, {
                useCORS: true,
                allowTaint: true,
                backgroundColor: null,
                scale: 2 // Higher resolution
            }).then(canvas => {
                const link = document.createElement('a');
                link.download = 'nature-meme-' + Date.now() + '.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
                
                downloadBtn.textContent = 'Download Meme';
                downloadBtn.disabled = false;
            }).catch(err => {
                console.error("Error generating image:", err);
                downloadBtn.textContent = 'Download Meme';
                downloadBtn.disabled = false;
                alert("Failed to generate meme. Try selecting a different template.");
            });
        }, 100);
    });

    // Init
    fetchMemes();
});

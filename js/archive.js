document.addEventListener('DOMContentLoaded', () => {
    let allArticles = [];
    let filteredArticles = [];
    let currentPage = 1;
    const articlesPerPage = 15;

    const gridContainer = document.getElementById('archive-grid');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const archiveHeading = document.getElementById('archive-heading');
    const searchInput = document.getElementById('search-input');

    // Leggiamo i parametri dall'URL (es. ?category=nba oppure ?search=clippers)
    const urlParams = new URLSearchParams(window.location.search);
    let currentCategory = urlParams.get('category') || 'all';
    let searchQuery = urlParams.get('search') || '';

    if (searchQuery && searchInput) {
        searchInput.value = searchQuery;
    }

    // Carichiamo gli articoli dal file JSON
    fetch('data/articoli.json')
        .then(response => response.json())
        .then(articles => {
            allArticles = articles;
            applyFiltersAndSearch();
            setupFilterButtonsUI();
        })
        .catch(err => console.error('Errore nel caricamento archivio:', err));

    // Funzione per filtrare e cercare
    function applyFiltersAndSearch() {
        filteredArticles = allArticles.filter(art => {
            // Filtro per categoria
            let matchesCategory = true;
            if (currentCategory !== 'all') {
                matchesCategory = art.category && art.category.toLowerCase() === currentCategory.toLowerCase();
            }

            // Filtro per ricerca (titolo, snippet, testo o tag)
            let matchesSearch = true;
            if (searchQuery) {
                const q = searchQuery.toLowerCase();
                const titleMatch = art.title && art.title.toLowerCase().includes(q);
                const snippetMatch = art.snippet && art.snippet.toLowerCase().includes(q);
                const contentMatch = art.content && art.content.toLowerCase().includes(q);
                const tagMatch = art.tags && art.tags.some(tag => tag.toLowerCase().includes(q));
                matchesSearch = titleMatch || snippetMatch || contentMatch || tagMatch;
            }

            return matchesCategory && matchesSearch;
        });

        currentPage = 1;
        renderPage();
    }

    // Renderizza la griglia degli articoli per la pagina corrente
    function renderPage() {
        if (!gridContainer) return;
        gridContainer.innerHTML = '';

        if (filteredArticles.length === 0) {
            gridContainer.innerHTML = `<p style="grid-column: span 3; text-align: center; color: #9ca3af; padding: 40px;">No articles found.</p>';
            if (paginationContainer) paginationContainer.style.display = 'none';
            return;
        }

        const startIndex = (currentPage - 1) * articlesPerPage;
        const endIndex = startIndex + articlesPerPage;
        const paginatedArticles = filteredArticles.slice(startIndex, endIndex);

        paginatedArticles.forEach(art => {
            const card = document.createElement('a');
            card.href = `article.html?id=${art.id}`;
            card.className = 'archive-card';

            const imgBg = art.coverImage ? `style="background-image: url('${art.coverImage}')"` : '';
            const imgText = art.coverImage ? '' : '[ ARTICLE THUMBNAIL ]';

            card.innerHTML = `
                <div class="archive-img-placeholder" ${imgBg}>${imgText}</div>
                <div class="archive-content">
                    <div class="article-tag">${art.category} • ${art.date || ''}</div>
                    <h3 class="archive-card-title">${art.title}</h3>
                    <p class="archive-snippet">${art.snippet || ''}</p>
                </div>
            `;
            gridContainer.appendChild(card);
        });

        updatePaginationControls();
    }

    // Aggiorna i bottoni di paginazione
    function updatePaginationControls() {
        const totalPages = Math.ceil(filteredArticles.length / articlesPerPage) || 1;
        if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
        
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage === totalPages;
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredArticles.length / articlesPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    // Gestione UI dei bottoni di filtro
    function setupFilterButtonsUI() {
        filterButtons.forEach(btn => {
            const filterVal = btn.getAttribute('data-filter');
            if (filterVal === currentCategory) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }

            btn.addEventListener('click', (e) => {
                e.preventDefault();
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentCategory = filterVal;
                
                if (archiveHeading) {
                    archiveHeading.textContent = currentCategory === 'all' ? 'All Articles' : `${currentCategory.toUpperCase()} Articles`;
                }

                applyFiltersAndSearch();
            });
        });
    }

    // Input di ricerca in tempo reale o invio
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchQuery = searchInput.value.trim();
                applyFiltersAndSearch();
            }
        });
    }
});

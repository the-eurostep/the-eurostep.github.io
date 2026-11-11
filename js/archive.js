document.addEventListener('DOMContentLoaded', function() {
    var allArticles = [];
    var filteredArticles = [];
    var currentPage = 1;
    var articlesPerPage = 15;

    var gridContainer = document.getElementById('archive-grid');
    var prevBtn = document.getElementById('prev-page');
    var nextBtn = document.getElementById('next-page');
    var pageInfo = document.getElementById('page-info');
    var filterButtons = document.querySelectorAll('.filter-btn');
    var archiveHeading = document.getElementById('archive-heading');
    var searchInput = document.getElementById('search-input');
    var paginationContainer = document.getElementById('pagination-container');

    var urlParams = new URLSearchParams(window.location.search);
    var currentCategory = (urlParams.get('category') || 'all').toLowerCase();
    var searchQuery = urlParams.get('search') || '';

    if (searchQuery && searchInput) {
        searchInput.value = searchQuery;
    }

    // Caricamento dati JSON
    fetch('data/articoli.json')
        .then(function(response) {
            return response.json();
        })
        .then(function(articles) {
            allArticles = articles || [];
            applyFiltersAndSearch();
        })
        .catch(function(err) {
            console.error('Errore caricamento:', err);
            allArticles = [];
            applyFiltersAndSearch();
        });

    function applyFiltersAndSearch() {
        filteredArticles = allArticles.filter(function(art) {
            var matchesCategory = true;
            if (currentCategory !== 'all') {
                var artCat = art.category ? art.category.toLowerCase().trim() : '';
                matchesCategory = (artCat === currentCategory);
            }

            var matchesSearch = true;
            if (searchQuery) {
                var q = searchQuery.toLowerCase();
                var titleMatch = art.title && art.title.toLowerCase().indexOf(q) !== -1;
                var snippetMatch = art.snippet && art.snippet.toLowerCase().indexOf(q) !== -1;
                matchesSearch = titleMatch || snippetMatch;
            }

            return matchesCategory && matchesSearch;
        });

        currentPage = 1;
        renderPage();
    }

    function renderPage() {
        if (!gridContainer) return;
        gridContainer.innerHTML = '';

        if (filteredArticles.length === 0) {
            gridContainer.innerHTML = '<p style="grid-column: span 3; text-align: center; color: #9ca3af; padding: 40px;">No articles found.</p>';
            if (paginationContainer) paginationContainer.style.display = 'none';
            return;
        }

        if (paginationContainer) paginationContainer.style.display = 'flex';

        var startIndex = (currentPage - 1) * articlesPerPage;
        var endIndex = startIndex + articlesPerPage;
        var paginatedArticles = filteredArticles.slice(startIndex, endIndex);

        paginatedArticles.forEach(function(art) {
            var card = document.createElement('a');
            card.href = 'article.html?id=' + art.id;
            card.className = 'archive-card';

            var imgBg = art.coverImage ? 'style="background-image: url(\'' + art.coverImage + '\')"' : '';
            var imgText = art.coverImage ? '' : '[ ARTICLE THUMBNAIL ]';
            var categoryText = art.category ? art.category : 'Article';
            var dateText = art.date ? art.date : '';

            card.innerHTML = 
                '<div class="archive-img-placeholder" ' + imgBg + '>' + imgText + '</div>' +
                '<div class="archive-content">' +
                    '<div class="article-tag">' + categoryText + ' • ' + dateText + '</div>' +
                    '<h3 class="archive-card-title">' + art.title + '</h3>' +
                    '<p class="archive-snippet">' + (art.snippet || '') + '</p>' +
                '</div>';

            gridContainer.appendChild(card);
        });

        updatePaginationControls();
    }

    function updatePaginationControls() {
        var totalPages = Math.ceil(filteredArticles.length / articlesPerPage) || 1;
        if (pageInfo) pageInfo.textContent = 'Page ' + currentPage + ' of ' + totalPages;
        
        if (prevBtn) prevBtn.disabled = (currentPage === 1);
        if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            var totalPages = Math.ceil(filteredArticles.length / articlesPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    filterButtons.forEach(function(btn) {
        var filterVal = btn.getAttribute('data-filter');
        if (filterVal === currentCategory) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }

        btn.addEventListener('click', function(e) {
            e.preventDefault();
            filterButtons.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            currentCategory = filterVal;
            
            if (archiveHeading) {
                archiveHeading.textContent = currentCategory === 'all' ? 'All Articles' : (currentCategory.toUpperCase() + ' Articles');
            }

            applyFiltersAndSearch();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchQuery = searchInput.value.trim();
                applyFiltersAndSearch();
            }
        });
    }
});

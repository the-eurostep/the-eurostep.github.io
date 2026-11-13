document.addEventListener('DOMContentLoaded', function () {
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
    var tagFilter = urlParams.get('tag') || '';

    if (searchQuery && searchInput) {
        searchInput.value = searchQuery;
    }

    /* ---------- utilità ---------- */

    // minuscolo e senza accenti: "Perché" e "perche" sono la stessa parola
    function norm(s) {
        return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
    }

    // Testo semplice a partire dall'HTML dell'articolo (DOMParser non esegue script né carica immagini)
    function htmlToText(html) {
        try {
            return new DOMParser().parseFromString(String(html || ''), 'text/html').body.textContent || '';
        } catch (e) {
            return String(html || '').replace(/<[^>]*>/g, ' ');
        }
    }

    function cssUrl(path) {
        return 'url("' + String(path).replace(/["\\\r\n]/g, '').replace(/ /g, '%20') + '")';
    }

    // Dal più recente al meno recente; a parità di data vale l'ordine nel file
    function sortArticles(list) {
        return list
            .map(function (a, i) { return { a: a, i: i }; })
            .sort(function (x, y) {
                var dx = x.a.date || '';
                var dy = y.a.date || '';
                if (dx !== dy) { return dx < dy ? 1 : -1; }
                return x.i - y.i;
            })
            .map(function (o) { return o.a; });
    }

    // Prepara una volta sola, per ogni articolo, il testo su cui si cerca
    function prepare(art) {
        var tags = Array.isArray(art.tags) ? art.tags : [];
        art._tags = tags.map(norm);
        art._haystack = norm([
            art.title, art.snippet, art.author, art.category, tags.join(' '), htmlToText(art.content)
        ].join(' \n '));
    }

    function updateHeading() {
        if (!archiveHeading) { return; }
        var text = currentCategory === 'all' ? 'All Articles' : (currentCategory.toUpperCase() + ' Articles');
        if (tagFilter) { text += ' · Tag: ' + tagFilter; }
        if (searchQuery) { text += ' · “' + searchQuery + '”'; }
        archiveHeading.textContent = text;
    }

    /* ---------- caricamento dati ---------- */
    fetch('data/articoli.json')
        .then(function (response) { return response.json(); })
        .then(function (articles) {
            allArticles = sortArticles(articles || []);
            allArticles.forEach(prepare);
            applyFiltersAndSearch();
        })
        .catch(function (err) {
            console.error('Errore caricamento:', err);
            allArticles = [];
            applyFiltersAndSearch();
        });

    function applyFiltersAndSearch() {
        var terms = norm(searchQuery).split(/\s+/).filter(Boolean);
        var wantedTag = norm(tagFilter).trim();

        filteredArticles = allArticles.filter(function (art) {
            if (currentCategory !== 'all') {
                var artCat = art.category ? art.category.toLowerCase().trim() : '';
                if (artCat !== currentCategory) { return false; }
            }
            if (wantedTag && art._tags.indexOf(wantedTag) === -1) { return false; }
            // tutte le parole cercate devono comparire (titolo, estratto, autore, categoria, tag o testo)
            return terms.every(function (t) { return art._haystack.indexOf(t) !== -1; });
        });

        currentPage = 1;
        updateHeading();
        renderPage();
    }

    function buildCard(art) {
        var card = document.createElement('a');
        card.href = 'article.html?id=' + encodeURIComponent(art.id);
        card.className = 'archive-card';

        var img = document.createElement('div');
        img.className = 'archive-img-placeholder';
        if (art.coverImage) {
            img.style.backgroundImage = cssUrl(art.coverImage);
        } else {
            img.textContent = '[ ARTICLE THUMBNAIL ]';
        }

        var content = document.createElement('div');
        content.className = 'archive-content';

        var tag = document.createElement('div');
        tag.className = 'article-tag';
        tag.textContent = (art.category || 'Article') + ' • ' + (art.date || '');

        var title = document.createElement('h3');
        title.className = 'archive-card-title';
        title.textContent = art.title || '';

        var snippet = document.createElement('p');
        snippet.className = 'archive-snippet';
        snippet.textContent = art.snippet || '';

        content.appendChild(tag);
        content.appendChild(title);
        content.appendChild(snippet);
        card.appendChild(img);
        card.appendChild(content);
        return card;
    }

    function renderPage() {
        if (!gridContainer) { return; }
        gridContainer.innerHTML = '';

        if (filteredArticles.length === 0) {
            var empty = document.createElement('p');
            empty.style.cssText = 'grid-column: 1 / -1; text-align: center; color: #9ca3af; padding: 40px;';
            empty.textContent = 'No articles found.';
            gridContainer.appendChild(empty);
            if (paginationContainer) { paginationContainer.style.display = 'none'; }
            return;
        }

        if (paginationContainer) { paginationContainer.style.display = 'flex'; }

        var startIndex = (currentPage - 1) * articlesPerPage;
        filteredArticles.slice(startIndex, startIndex + articlesPerPage).forEach(function (art) {
            gridContainer.appendChild(buildCard(art));
        });

        updatePaginationControls();
    }

    function updatePaginationControls() {
        var totalPages = Math.ceil(filteredArticles.length / articlesPerPage) || 1;
        if (pageInfo) { pageInfo.textContent = 'Page ' + currentPage + ' of ' + totalPages; }
        if (prevBtn) { prevBtn.disabled = (currentPage === 1); }
        if (nextBtn) { nextBtn.disabled = (currentPage >= totalPages); }
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', function () {
            if (currentPage > 1) {
                currentPage--;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function () {
            var totalPages = Math.ceil(filteredArticles.length / articlesPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderPage();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        });
    }

    filterButtons.forEach(function (btn) {
        var filterVal = btn.getAttribute('data-filter');
        if (filterVal === currentCategory) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            filterButtons.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            currentCategory = filterVal;
            applyFiltersAndSearch();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                searchQuery = searchInput.value.trim();
                tagFilter = '';   // una nuova ricerca sostituisce il filtro per tag
                applyFiltersAndSearch();
            }
        });
    }
});

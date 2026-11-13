document.addEventListener('DOMContentLoaded', function () {

    // Percorso immagine -> valore CSS sicuro (niente virgolette che rompono lo stile)
    function cssUrl(path) {
        return 'url("' + String(path).replace(/["\\\r\n]/g, '').replace(/ /g, '%20') + '")';
    }

    // Dal più recente al meno recente; a parità di data vale l'ordine nel file (il nuovo sta in cima)
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

    // Costruisce una scheda articolo con il DOM (il testo non viene mai interpretato come HTML)
    function buildCard(art, cls) {
        var card = document.createElement('a');
        card.href = 'article.html?id=' + encodeURIComponent(art.id);
        card.className = cls.card;

        var img = document.createElement('div');
        img.className = cls.img;
        if (art.coverImage) {
            img.style.backgroundImage = cssUrl(art.coverImage);
        } else {
            img.textContent = '[ ARTICLE THUMBNAIL ]';
        }

        var content = document.createElement('div');
        content.className = cls.content;

        var tag = document.createElement('div');
        tag.className = 'article-tag';
        tag.textContent = art.category || '';

        var title = document.createElement('h3');
        title.className = cls.title;
        title.textContent = art.title || '';

        content.appendChild(tag);
        content.appendChild(title);
        card.appendChild(img);
        card.appendChild(content);
        return card;
    }

    fetch('data/articoli.json')
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (!data || data.length === 0) { return; }
            var articles = sortArticles(data);

            // 1. Articolo in evidenza (il più recente)
            var featured = articles[0];
            var featuredLink = document.getElementById('featured-article-link');
            var featuredTag = document.getElementById('featured-tag');
            var featuredTitle = document.getElementById('featured-title');
            var featuredSnippet = document.getElementById('featured-snippet');
            var featuredImg = document.getElementById('featured-img');

            if (featuredLink && featured) {
                featuredLink.href = 'article.html?id=' + encodeURIComponent(featured.id);
                var firstTag = (featured.tags && featured.tags[0]) ? featured.tags[0] : 'Analysis';
                featuredTag.textContent = (featured.category || 'Article') + ' • ' + firstTag;
                featuredTitle.textContent = featured.title || '';
                featuredSnippet.textContent = featured.snippet || '';

                if (featured.coverImage) {
                    featuredImg.style.backgroundImage = cssUrl(featured.coverImage);
                    featuredImg.textContent = '';
                } else {
                    featuredImg.textContent = '[ FEATURED ARTICLE IMAGE ]';
                }
            }

            // 2. Colonna laterale (articoli 2, 3, 4)
            var sideContainer = document.getElementById('side-articles-container');
            if (sideContainer) {
                sideContainer.innerHTML = '';
                articles.slice(1, 4).forEach(function (art) {
                    sideContainer.appendChild(buildCard(art, {
                        card: 'side-article-card', img: 'side-img-placeholder',
                        content: 'side-content', title: 'side-article-title'
                    }));
                });
            }

            // 3. Griglia in basso (articoli 5, 6, 7)
            var gridContainer = document.getElementById('secondary-articles-container');
            if (gridContainer) {
                gridContainer.innerHTML = '';
                articles.slice(4, 7).forEach(function (art) {
                    gridContainer.appendChild(buildCard(art, {
                        card: 'grid-article-card', img: 'grid-img-placeholder',
                        content: 'grid-content', title: 'grid-title'
                    }));
                });
            }
        })
        .catch(function (err) { console.error('Errore nel caricamento degli articoli:', err); });

    // Barra di ricerca: Invio -> pagina dei risultati
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                var query = searchInput.value.trim();
                if (query) {
                    window.location.href = 'see-more-articles.html?search=' + encodeURIComponent(query);
                }
            }
        });
    }
});

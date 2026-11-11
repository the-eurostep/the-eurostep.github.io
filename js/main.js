document.addEventListener('DOMContentLoaded', () => {
    // Carichiamo gli articoli dal file JSON
    fetch('data/articoli.json')
        .then(response => response.json())
        .then(articles => {
            if (!articles || articles.length === 0) return;

            // 1. Articolo in Evidenza (Il più recente -> primo elemento dell'array)
            const featured = articles[0];
            const featuredLink = document.getElementById('featured-article-link');
            const featuredTag = document.getElementById('featured-tag');
            const featuredTitle = document.getElementById('featured-title');
            const featuredSnippet = document.getElementById('featured-snippet');
            const featuredImg = document.getElementById('featured-img');

            if (featuredLink && featured) {
                featuredLink.href = `article.html?id=${featured.id}`;
                featuredTag.textContent = `${featured.category} • ${featured.tags[0] || 'Analysis'}`;
                featuredTitle.textContent = featured.title;
                featuredSnippet.textContent = featured.snippet;

                if (featured.coverImage) {
                    featuredImg.style.backgroundImage = `url('${featured.coverImage}')`;
                    featuredImg.textContent = '';
                } else {
                    featuredImg.textContent = '[ FEATURED ARTICLE IMAGE ]';
                }
            }

            // 2. Colonna Laterale (Prossimi 3 articoli: indice 1, 2, 3)
            const sideContainer = document.getElementById('side-articles-container');
            if (sideContainer) {
                sideContainer.innerHTML = ''; // Puliamo il container
                const sideArticles = articles.slice(1, 4);

                sideArticles.forEach(art => {
                    const sideCard = document.createElement('a');
                    sideCard.href = `article.html?id=${art.id}`;
                    sideCard.className = 'side-article-card';

                    const imgBg = art.coverImage ? `style="background-image: url('${art.coverImage}')"` : '';
                    const imgText = art.coverImage ? '' : '[ ARTICLE THUMBNAIL ]';

                    sideCard.innerHTML = `
                        <div class="side-img-placeholder" ${imgBg}>${imgText}</div>
                        <div class="side-content">
                            <div class="article-tag">${art.category}</div>
                            <h3 class="side-article-title">${art.title}</h3>
                        </div>
                    `;
                    sideContainer.appendChild(sideCard);
                });
            }

            // 3. Griglia Secondaria in Basso (Prossimi 3 articoli: indice 4, 5, 6)
            const gridContainer = document.getElementById('secondary-articles-container');
            if (gridContainer) {
                gridContainer.innerHTML = ''; // Puliamo il container
                const gridArticles = articles.slice(4, 7);

                gridArticles.forEach(art => {
                    const gridCard = document.createElement('a');
                    gridCard.href = `article.html?id=${art.id}`;
                    gridCard.className = 'grid-article-card';

                    const imgBg = art.coverImage ? `style="background-image: url('${art.coverImage}')"` : '';
                    const imgText = art.coverImage ? '' : '[ ARTICLE THUMBNAIL ]';

                    gridCard.innerHTML = `
                        <div class="grid-img-placeholder" ${imgBg}>${imgText}</div>
                        <div class="grid-content">
                            <div class="article-tag">${art.category}</div>
                            <h3 class="grid-title">${art.title}</h3>
                        </div>
                    `;
                    gridContainer.appendChild(gridCard);
                });
            }
        })
        .catch(err => console.error('Errore nel caricamento degli articoli:', err));

    // Gestione della Barra di Ricerca (Searchbar)
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    window.location.href = `see-more-articles.html?search=${encodeURIComponent(query)}`;
                }
            }
        });
    }
});

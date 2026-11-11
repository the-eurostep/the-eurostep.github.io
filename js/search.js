document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                var query = searchInput.value.trim();
                if (query) {
                    window.location.href = 'see-more-articles.html?search=' + encodeURIComponent(query);
                }
            }
        });
    }
});

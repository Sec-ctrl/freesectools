document.addEventListener('DOMContentLoaded', () => {
    // Search functionality
    const searchInput = document.querySelector('#searchInput');
    const categoryFilter = document.querySelector('#categoryFilter');
    const blogCards = document.querySelectorAll('.card');

    searchInput.addEventListener('input', () => {
        filterBlogs();
    });

    categoryFilter.addEventListener('change', () => {
        filterBlogs();
    });

    function filterBlogs() {
        const searchTerm = searchInput.value.toLowerCase();
        const selectedCategory = categoryFilter.value;

        blogCards.forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const category = card.querySelector('.badge').textContent;

            // Check if blog matches search term and category filter
            const matchesSearch = title.includes(searchTerm);
            const matchesCategory = selectedCategory === "" || category === selectedCategory;

            if (matchesSearch && matchesCategory) {
                card.parentElement.style.display = 'block'; // Show the card
            } else {
                card.parentElement.style.display = 'none'; // Hide the card
            }
        });
    }
});
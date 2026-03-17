document.addEventListener('DOMContentLoaded', () => {
    const favoritesContainer = document.getElementById('favorites-grid');
    const emptyState = document.getElementById('favorites-empty');
    const favorites = JSON.parse(localStorage.getItem('myFavorites')) || [];

    if (favorites.length === 0) {
        emptyState.style.display = 'block';
        return;
    }

    favorites.forEach(id => {
        const recipe = allRecipes[id];
        if (recipe) {
            const card = document.createElement('article');
            card.className = 'recipe-card';
            card.innerHTML = `
                <div class="card-image-container">
                    <img src="${recipe.image}" alt="${recipe.title}">
                </div>
                <div class="card-content">
                    <h4>${recipe.title}</h4>
                    <div style="display:flex; gap:10px; margin-top:15px; flex-wrap:wrap;">
                        <a href="recipe-details.html?id=${id}" class="cta-button" style="font-size:0.85rem; padding:8px 16px;">رؤية الطريقة</a>
                        <button onclick="removeFromFavorites('${id}')" class="btn-remove-fav">🗑️ حذف</button>
                    </div>
                </div>
            `;
            favoritesContainer.appendChild(card);
        }
    });
});

// دالة الحذف من المفضلة
function removeFromFavorites(id) {
    let favorites = JSON.parse(localStorage.getItem('myFavorites')) || [];
    favorites = favorites.filter(favId => favId !== id);
    localStorage.setItem('myFavorites', JSON.stringify(favorites));
    location.reload();
}
// Modal
const modal = document.getElementById('reviewModal');
const openBtn = document.getElementById('openReviewModal');
const closeBtn = document.getElementById('closeModal');
if(openBtn) openBtn.onclick = () => modal.style.display = 'flex';
if(closeBtn) closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = e => { if(e.target === modal) modal.style.display = 'none'; };

// ⭐ Rating System
const stars = document.querySelectorAll('#starRating span');
const ratingInput = document.getElementById("ratingInput");
stars.forEach(star => {
    star.addEventListener("mouseover", () => highlight(star.dataset.value));
    star.addEventListener("click", () => { ratingInput.value = star.dataset.value; highlight(star.dataset.value); });
});
document.getElementById("starRating").addEventListener("mouseleave", () => highlight(ratingInput.value));
function highlight(count){
    stars.forEach(s => { s.style.color = s.dataset.value <= count ? "#ffc107" : "#ccc"; });
}

// AJAX Load More Reviews
const loadMoreBtn = document.getElementById('loadMoreBtn');
const reviewsGrid = document.getElementById('reviewsGrid');

if(loadMoreBtn){
    loadMoreBtn.addEventListener('click', () => {
        let page = loadMoreBtn.dataset.nextPage;
        const url = "{% url 'tours:load_more_reviews' tour.id %}?page=" + page;

        fetch(url)
        .then(res => res.json())
        .then(data => {
            reviewsGrid.insertAdjacentHTML('beforeend', data.html);
            if(data.has_next){ loadMoreBtn.dataset.nextPage = parseInt(page) + 1; }
            else{ loadMoreBtn.style.display = 'none'; }
        }).catch(err => console.error(err));
    });
}
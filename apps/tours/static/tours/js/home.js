document.addEventListener("DOMContentLoaded", () => {
// Hero fade-in
const heroTitle = document.querySelector('.hero-title');
const heroSubtitle = document.querySelector('.hero-subtitle');
const heroBtn = document.querySelector('.hero-btn');

setTimeout(() => { heroTitle.style.transition = 'all 1s ease'; heroTitle.style.opacity = 1; heroTitle.style.transform = 'translateY(0)'; }, 300);
setTimeout(() => { heroSubtitle.style.transition = 'all 1s ease'; heroSubtitle.style.opacity = 1; heroSubtitle.style.transform = 'translateY(0)'; }, 700);
setTimeout(() => { heroBtn.style.transition = 'all 0.6s ease'; heroBtn.style.transform = 'scale(1)'; }, 1200);

// Feature card hover
document.querySelectorAll('.feature-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
    card.style.transform = 'translateY(-10px)';
    card.style.boxShadow = '0 12px 25px rgba(0,0,0,0.2)';
    card.querySelector('img').style.transform = 'scale(1.1)';
    });
    card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0)';
    card.style.boxShadow = '0 8px 20px rgba(0,0,0,0.1)';
    card.querySelector('img').style.transform = 'scale(1)';
    });
});

// Scroll reveal for about
const aboutSection = document.querySelector('.about');
window.addEventListener('scroll', () => {
    const scrollPos = window.scrollY + window.innerHeight;
    if(scrollPos > aboutSection.offsetTop + 100) {
    aboutSection.style.transition = 'all 1s ease';
    aboutSection.style.opacity = 1;
    aboutSection.style.transform = 'translateY(0)';
    }
});
});
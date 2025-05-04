// Allbirds-inspired admin UI enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Add subtle hover animations to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.05)';
        });
    });
    
    // Enhance form fields with subtle animations
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('input-focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('input-focused');
        });
    });
    
    // Add smooth transitions to sidebar menu items
    const navItems = document.querySelectorAll('.nav-sidebar .nav-item');
    navItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.querySelector('.nav-link').classList.add('nav-link-hover');
        });
        
        item.addEventListener('mouseleave', function() {
            this.querySelector('.nav-link').classList.remove('nav-link-hover');
        });
    });
});

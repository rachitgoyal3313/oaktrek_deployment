window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Dropdown toggle function
function toggleDropdown(dropdownId) {
    // Close all dropdowns first
    const allDropdowns = document.querySelectorAll('.custom-dropdown');
    allDropdowns.forEach(dropdown => {
        if(dropdown.id !== dropdownId && dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    });

    // Toggle the clicked dropdown
    const dropdown = document.getElementById(dropdownId);
    dropdown.classList.toggle('show');
}

// Close dropdowns when clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.nav-link')) {
        const dropdowns = document.getElementsByClassName("custom-dropdown");
        for (let dropdown of dropdowns) {
            if (dropdown.classList.contains('show') && !dropdown.contains(event.target)) {
                dropdown.classList.remove('show');
            }
        }
    }
}
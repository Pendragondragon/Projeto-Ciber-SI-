    // Toggle Mobile Menu
    const menuBtn = document.getElementById('menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    menuBtn.addEventListener('click', () => {
        mobileMenu.hidden = !mobileMenu.hidden;
    });

    // Toggle Desktop Profile Dropdown
    const profileBtn = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');

    profileBtn.addEventListener('click', (e) => {
        userMenu.style.display = userMenu.style.display === 'block' ? 'none' : 'block';
        e.stopPropagation();
    });

    // Toggle Mobile Profile Accordion
    const userLink = document.querySelector('.user-link');
    userLink.addEventListener('click', function(e) {
        e.preventDefault();
        this.classList.toggle('active');
        const panel = this.querySelector('.panel');
        panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
    });

    // Close dropdowns if clicking outside
    window.onclick = (event) => {
        if (!event.target.matches('#user-menu-button') && !event.target.closest('.avatar-placeholder')) {
            userMenu.style.display = 'none';
        }
    }

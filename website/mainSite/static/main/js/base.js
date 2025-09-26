document.addEventListener('DOMContentLoaded', () => {
    const themeToggles = document.querySelectorAll('#themeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    const bodyTeg = document.body;
    
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggles.forEach(themeToggle => {  
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });   
    });
    
    // Скрытие header при скролле
    let lastScrollY = window.scrollY;
    const header = document.getElementById('header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > lastScrollY && window.scrollY > 100) {
            header.classList.add('hidden');
        } else {
            header.classList.remove('hidden');
        }
        
        lastScrollY = window.scrollY;
    });

    burgerButton = document.querySelector('.burger-menu')
    sidebar = document.querySelector('.sidebar')
    burgerButton.addEventListener('click', () => {
        sidebar.classList.toggle('active')
        burgerButton.classList.toggle('active')
        bodyTeg.classList.toggle('non-scroll')
    })
})

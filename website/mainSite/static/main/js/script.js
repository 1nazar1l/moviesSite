function ready(){
    const mainH1 = document.querySelector("main .hero h1")
    const mainP = document.querySelector("main .hero p")
    const mainSearch = document.querySelector("main .hero .search_block")

    mainH1.classList.add("active");
    mainP.classList.add("active");
    mainSearch.classList.add("active");
}

document.addEventListener("DOMContentLoaded", ready);

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
    
    heroBlock = document.querySelector("main .hero")
    const section1 = document.querySelector("main .section1")
    const section2 = document.querySelector("main .section2")
    const section3 = document.querySelector("main .section3")
    
    document.addEventListener('scroll', function(event) {
        let rest = heroBlock.getBoundingClientRect()
        
        if (rest.y <= -200) {
            section1.classList.add("active")
        }
        if (rest.y <= -600) {
            section2.classList.add("active")
        }
    
        if (rest.y <= -1100) {
            section3.classList.add("active")
        }
    })

    burgerButton = document.querySelector('.burger-menu')
    sidebar = document.querySelector('.sidebar')
    burgerButton.addEventListener('click', () => {
        sidebar.classList.toggle('active')
        burgerButton.classList.toggle('active')
        bodyTeg.classList.toggle('non-scroll')
    })
})

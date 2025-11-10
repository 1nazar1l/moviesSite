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
    heroBlock = document.querySelector("main .hero")
    const section1 = document.querySelector("main .section1")
    const section2 = document.querySelector("main .section2")
    const section3 = document.querySelector("main .section3")
    let rest = heroBlock.getBoundingClientRect()
    
    section1.classList.add("active")

    if (rest.y <= -400) {
            section2.classList.add("active")
        }
    
    if (rest.y <= -700) {
        section3.classList.add("active")
    }

    document.addEventListener('scroll', function(event) {
        let rest = heroBlock.getBoundingClientRect()
        
        if (rest.y <= -400) {
            section2.classList.add("active")
        }
    
        if (rest.y <= -700) {
            section3.classList.add("active")
        }
    })
})
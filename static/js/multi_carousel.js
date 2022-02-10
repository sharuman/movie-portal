let carousels=document.getElementsByClassName("carousel slide")

let carouselDocId=""
for (var i = 0; i < carousels.length; i++) {
    let carousel = carousels.item(i)
    carouselDocId="#"+carousel.id
    let items = document.querySelectorAll(carouselDocId+ ' .carousel-item')
    items.forEach((el) => {
        const minPerSlide = 7
        let next = el.nextElementSibling
        for (var i=1; i<minPerSlide; i++) {
            if (!next) {
                // wrap carousel by using first child
                next = items[0]
            }
            let cloneChild = next.cloneNode(true)
            el.appendChild(cloneChild.children[0])
            next = next.nextElementSibling
        }
    })

}


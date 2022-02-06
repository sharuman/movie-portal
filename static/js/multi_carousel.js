let items = document.querySelectorAll('#featuredCarousel .carousel-item')

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

let items2 = document.querySelectorAll('#recommendedCarousel .carousel-item')

items2.forEach((el) => {
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

let items3 = document.querySelectorAll('#genre1Carousel .carousel-item')

items3.forEach((el) => {
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

let items4 = document.querySelectorAll('#genre2Carousel .carousel-item')

items4.forEach((el) => {
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
/*
$('#featuredCarousel').carousel({
  interval: 1000,
  wrap: false
});

 $('#featuredCarousel').on('slid.bs.carousel', '', function() {
  var $this = $(this);

  $this.children('.carousel-control').show();

  if($('.carousel-inner .item:first').hasClass('active')) {
    $this.children('.carousel-control-prev').hide();
  } else if($('.carousel-inner .item:last').hasClass('active')) {
    $this.children('.carousel-control-next').hide();
  }

});*/
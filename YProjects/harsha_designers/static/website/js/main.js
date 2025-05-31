$(window).scroll(function(e) {
  // sticky header //
  e.preventDefault();
  
  if ($(this).scrollTop() > 30) {
      $('.head').addClass('shead');
      } else {
      $('.head').removeClass('shead');
      }
  });


  function reloadWithoutScroll(e) {
    e.preventDefault();
  
    const scrollY = window.scrollY;
  
    location.reload();
  
    window.scrollTo(0, scrollY);

    
  }

  // phone menu

  $(".phn-menu > .mnlik").on('click', function(e) {
    e.preventDefault();
    $(".sld-menu").fadeToggle();
    $(this).toggleClass('opened');
    $(".head").toggleClass('shadw');
});


$('.sld-list > li > a').on('click', function(e) {
    e.preventDefault();
    $(".mnlik").removeClass('opened');
    $('.sld-menu').fadeOut();
}); 

$(".sld-list > li > a").on('click', function(e) {
  e.preventDefault();
  $(this).parent().addClass('over');
  $(this).parent().siblings().removeClass('over');
});



// showSlides();



    let slideIndex = 0;
    const slides = document.getElementsByClassName("slide");
    const dots = document.getElementsByClassName("dot");
    const slidesContainer = document.querySelector(".slides-container");
    
    showSlides();

    function showSlides() {
      for (let i = 0; i < dots.length; i++) {
        dots[i].classList.remove("active");
      }

      slideIndex++;
      if (slideIndex > slides.length) {
        slideIndex = 1;
      }

      // Move the container to the left by the width of one slide
      slidesContainer.style.transform = `translateX(-${(slideIndex - 1) * 100}%)`;

      // Set active class on the corresponding dot
      dots[slideIndex - 1].classList.add("active");

      setTimeout(showSlides, 3000); // Change slide every 3 seconds
    }

    function currentSlide(n) {
      slideIndex = n - 1;
      showSlides();
    }



// projects

$(document).ready(function(){

    $('.product-carousel').owlCarousel({
      loop: true,
      margin: 20,
      nav: true,
      dots: false,
      autoplay: true,
      autoplayTimeout: 4000,
      autoplayHoverPause: true,
      navText: ['<', '>'],
      responsive: {
        0: { items: 1 },
        600: { items: 2 },
        1000: { items: 3 }
      }
    });
  
    $(".prj-prev button").click(function(){
      $(".product-carousel").trigger('prev.owl.carousel');
    });
  
    $(".prj-nex button").click(function(){
      $(".product-carousel").trigger('next.owl.carousel');
    });
    $('.project-card > a').click(function(e){
        e.preventDefault();
    })
  
  });  



// footer

$('.footer > div > ul > li > a').click(function(e){
    e.preventDefault();
})
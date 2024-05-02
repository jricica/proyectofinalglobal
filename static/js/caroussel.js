$(document).ready(function(){
    $('#carouselExampleIndicators').carousel({
        interval: 5000, // Cambia la diapositiva cada 5 segundos
        pause: "hover" // Pausa el carrusel al pasar el mouse sobre él
    });

    $('.carousel-nav-btn').click(function(){
        var targetSlide = $(this).attr('data-slide-to');
        $('#carouselExampleIndicators').carousel(parseInt(targetSlide));
    });
});

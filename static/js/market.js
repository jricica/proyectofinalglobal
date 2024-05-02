function updateMarketData() {
    $.ajax({
        url: 'https://api.polygon.io/v2/aggs/ticker/INDU/prev?unadjusted=true&apiKey=M3uZw7o7Z_74c3oyzCCc6chvHf1ZhGQh',
        method: 'GET',
        success: function(data) {
            $('#dowjones-price').text(data.results[0].c);
        },
        error: function(error) {
            console.error('Error al obtener los datos del Dow Jones:', error);
        }
    });
    
    $.ajax({
        url: 'https://api.polygon.io/v2/aggs/ticker/NQ/prev?unadjusted=true&apiKey=M3uZw7o7Z_74c3oyzCCc6chvHf1ZhGQh',
        method: 'GET',
        success: function(data) {
            $('#nasdaq-price').text(data.results[0].c);
        },
        error: function(error) {
            console.error('Error al obtener los datos del NASDAQ:', error);
        }
    });

    $.ajax({
        url: 'https://api.fastforex.io/fetch-one?from=USD&to=GTQ&api_key=15118b75fb-336262ee91-scv6ul',
        method: 'GET',
        success: function(data) {
            $('#usd-compra').text('Compra: ' + data.result.GTQ);
            $('#usd-venta').text('Venta: ' + data.result.GTQ);
        },
        error: function(error) {
            console.error('Error al obtener los datos de divisas:', error);
        }
    });
    
    $.ajax({
        url: 'https://api.fastforex.io/fetch-one?from=EUR&to=GTQ&api_key=15118b75fb-336262ee91-scv6ul',
        method: 'GET',
        success: function(data) {
            $('#eur-compra').text('Compra: ' + data.result.GTQ);
            $('#eur-venta').text('Venta: ' + data.result.GTQ);
        },
        error: function(error) {
            console.error('Error al obtener los datos de divisas:', error);
        }
    });
}

function countdown() {
    var remainingTimeInSeconds = parseInt('{{ remaining_time.total_seconds() }}');
    var countdownElement = document.getElementById('countdown');

    var intervalId = setInterval(function() {
        if (remainingTimeInSeconds <= 0) {
            clearInterval(intervalId);
            countdownElement.innerHTML = 'Session expired';
        } else {
            var hours = Math.floor(remainingTimeInSeconds / 3600);
            var minutes = Math.floor((remainingTimeInSeconds % 3600) / 60);
            var seconds = remainingTimeInSeconds % 60;

            countdownElement.innerHTML = hours + 'h ' + minutes + 'm ' + seconds + 's';
            remainingTimeInSeconds--;
        }
    }, 1000);
}

countdown(); // Inicia el contador

updateMarketData(); // Actualiza los datos del mercado al cargar la página
setInterval(updateMarketData, 60000); // Actualiza los datos del mercado cada minuto (60000 milisegundos)

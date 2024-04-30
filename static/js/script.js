function sendMessage() {
    var userInput = document.getElementById("user-input").value;
    document.getElementById("chat-output").innerHTML += "<div><strong>Tú:</strong> " + userInput + "</div>";
    document.getElementById("user-input").value = "";
    
    // Enviar el mensaje al servidor
    fetch('/chatbot', {
        method: 'POST',
        body: new URLSearchParams({
            'user_message': userInput
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById("chat-output").innerHTML += "<div><strong>Chatbot:</strong> " + data + "</div>";
    });
}

document.getElementById("loan-form").addEventListener("submit", function(event) {
    event.preventDefault();
    var amount = document.getElementById("amount").value;
    var duration = document.getElementById("duration").value;
    // Aquí podrías enviar la solicitud de préstamo al servidor...
});

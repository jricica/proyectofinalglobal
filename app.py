
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Aquí iría la lógica del chatbot
    user_message = request.form['user_message']
    # Lógica del chatbot aquí...
    # Por simplicidad, devolvemos un mensaje de ejemplo
    response = "Hola, soy el chatbot del banco. ¿En qué puedo ayudarte?"
    return response

if __name__ == "__main__":
    app.run(debug=True, port=8080)
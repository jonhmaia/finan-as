from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')  # Certifique-se de que o caminho para Config está correto
db = SQLAlchemy(app)

from routes import *

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from backend.api_routes import api
from flask import render_template

app = Flask(__name__)

# Register the blueprint for API routes
# app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return render_template('templates/index.html')

@app.route('/register_user')
def register():
    return render_template('register_user.html')

if __name__ == '__main__':
    app.run()

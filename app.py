from flask import Flask
import api  # Import API routes from api.py

app = Flask(__name__)

# Existing route
@app.route('/')
def index():
    return 'Website Coming Soon!'

# Include API routes from api.py
api.register_api_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request
from datetime import datetime
from dotenv import load_dotenv
import os
import pymongo
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

# Get the MongoDB URI
Mongo_URI = os.getenv('Mongo_URI')

app = Flask(__name__)

# Initialize MongoDB connection with error handling
try:
    if not Mongo_URI:
        raise ValueError("Mongo_URI not found in .env file")
    
    client = pymongo.MongoClient(Mongo_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    print("✅ Connected to MongoDB Atlas successfully!")
    
    db = client["flask_users"]
    users_collection = db["users"]
    
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file")
    exit(1)
except pymongo.errors.OperationFailure as e:
    print(f"❌ Authentication failed: {e}")
    print("Please check your MongoDB username and password")
    exit(1)
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"❌ Connection timeout: {e}")
    print("Please check your internet connection and MongoDB Atlas settings")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)

@app.route('/')
def home():
    day_of_week = datetime.now().strftime("%A")
    current_time = datetime.now().strftime("%I:%M %p")
    return render_template('index.html', day_of_week=day_of_week, current_time=current_time)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Validate passwords match
    if password != confirm_password:
        return """
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>❌ Passwords do not match!</h2>
            <a href="/" style="color: #667eea; text-decoration: none;">← Go Back</a>
        </body>
        </html>
        """, 400

    # Hash the password for security
    hashed_password = generate_password_hash(password)

    new_user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now()
    }

    try:
        # Check if email already exists
        if users_collection.find_one({"email": email}):
            return """
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h2>❌ Email already registered!</h2>
                <a href="/" style="color: #667eea; text-decoration: none;">← Go Back</a>
            </body>
            </html>
            """, 400
        
        # Insert the new user
        users_collection.insert_one(new_user)
        
        # Render the submit.html template with user data
        return render_template('submit.html', name=name, email=email)
        
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>❌ Error: {str(e)}</h2>
            <a href="/" style="color: #667eea; text-decoration: none;">← Go Back</a>
        </body>
        </html>
        """, 500

if __name__ == '__main__':
    app.run(debug=True)

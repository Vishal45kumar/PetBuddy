from flask import Flask, request, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os
import uuid
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

# Gemini API Configuration
# Gemini API Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('models/gemini-1.5-flash-002')


app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# MongoDB Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client.travel_reviews
users_collection = db.users
reviews_collection = db.reviews
ratings_collection = db.ratings

# USER AUTHENTICATION
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    address = data.get("address")
    phone = data.get("phone")
    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    users_collection.insert_one ({
        "name": name,
        "email": email,
        "password": hashed_password,
        "address": address,
        "phone": phone
    })

    access_token = create_access_token(identity=email)

    return jsonify({
        "message": "Signup successful!",
        "token": access_token,
        "name": name
    }), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    user = users_collection.find_one({"email": email})
    if user and bcrypt.check_password_hash(user["password"], password):
        access_token = create_access_token(identity=user["email"])
        return jsonify({"token": access_token, "message": "Login successful!", "name": user["name"]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({"message": f"Hello, {get_jwt_identity()}"}), 200

# PHOTO UPLOADS
@app.route("/upload_photos", methods=["POST"])
def upload_photos():
    if "photos" not in request.files:
        return jsonify({"error": "No photos uploaded"}), 400
    files = request.files.getlist("photos")
    urls = []
    for file in files:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        urls.append(f"/uploads/{filename}")
    return jsonify({"message": "Photos uploaded successfully!", "urls": urls}), 201

@app.route("/uploads/<filename>")
def get_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()  # Get the email of the currently authenticated user
    user = users_collection.find_one({"email": current_user})
    
    if user:
        response_data = {
            "name": user["name"],
            "email": user["email"],
        }
        return jsonify(response_data)
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/list_models", methods=["GET"])
def list_models():
    try:
        # List available models and convert the generator into a list
        models = list(genai.list_models())  # Convert the generator to a list
        print(models)  # Prints the list of available models to the console for debugging
        return jsonify(models)  # Returns the models as a JSON response to the client
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate_diet", methods=["POST"])
def generate_diet():
    data = request.json

    # Getting inputs from the user
    pet_name = data.get("pet_name")
    breed = data.get("breed")
    age = data.get("age")
    health = data.get("health")
    pet_category = data.get("pet_category")
    gender=data.get("gender")

    # Ensure all necessary data is provided
    if not all([pet_name,breed,age,health]):
        return jsonify({"error": "pet name , age, breed and health status are required."}), 400

    # Create a prompt based on the user inputs
    prompt = f"""
    Generate a personalized diet plan for a pet based on the following:
    - Pet name: {pet_name}
    - Breed: ${breed}
    - Pet Age: {age}
    - Health Status: {health}
    - Pet category: {pet_category}
    -Pet Gender:{gender}

    Please include:
- Recommended daily meals (breakfast, lunch, dinner)
- Portion sizes
- Nutritional breakdown (protein, carbs, fats, vitamins)
- Any specific supplements or treats
- Notes for special dietary needs if applicable (based on health status)
    """

    try:
        # Call Gemini API to generate the itinerary
        response = gemini_model.generate_content(prompt)
        
        # Check if the response is valid
        if response.text:
            return jsonify({"diet": response.text})
        else:
            return jsonify({"error": "Failed to generate diet, no content returned."}), 500
    except Exception as e:
        # Return any exception that occurs
        return jsonify({"error": str(e)}), 500

@app.route("/generate_disease", methods=["POST"])
def generate_disease():
    data = request.json

    # Getting inputs from the user
    pet_name = data.get("pet_name")
    breed = data.get("breed")
    age = data.get("age")
    health = data.get("health")
    pet_category = data.get("pet_category")
    gender=data.get("gender")

    # Ensure all necessary data is provided
    if not all([pet_name,breed,age,health]):
        return jsonify({"error": "pet name , age, breed and symptoms are required."}), 400

    # Create a prompt based on the user inputs
    prompt = f"""
    Generate a disease prediction for a pet based on the following:
    - Pet name: {pet_name}
    - Breed: ${breed}
    - Pet Age: {age}
    - Pet Symptoms: {health}
    - Pet category: {pet_category}
    -Pet Gender:{gender}

    Based on these details, please give a medical diagnosis using the symptoms of the pet and give the aspects to take care of.


    """

    try:
        # Call Gemini API to generate the itinerary
        response = gemini_model.generate_content(prompt)

        # Check if the response is valid
        if response.text:
            return jsonify({"disease": response.text})
        else:
            return jsonify({"error": "Failed to generate diet, no content returned."}), 500
    except Exception as e:
        # Return any exception that occurs
        return jsonify({"error": str(e)}), 500
    

@app.route("/send-message", methods=["POST"])
def send_message():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Log the received data for debugging
        app.logger.info(f"Received message from {name} ({email}): {message}")

        if not name or not email or not message:
            raise ValueError("Name, email, and message are required.")

        msg_body = f"""
        📬 New message from Pet Buddy:

        👤 Name: {name}
        📧 Email: {email}
        📝 Message:
        {message}
        """

        # 🔁 CHANGE THIS TO YOUR EMAIL
        sender_email = "petbuddy25@gmail.com"   # <-- your Gmail (same one used for login)
        receiver_email = "petbuddy25@gmail.com"  # <-- where you want to receive the messages
        app_password = "gblk qblb tbxu pade"  # <-- your Gmail app password

        msg = MIMEText(msg_body)
        msg["Subject"] = "New Contact Message"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Attempt to send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)  # 🔒 login securely
            server.send_message(msg)

        app.logger.info("Message sent successfully")
        return jsonify({"message": "Message sent successfully!"}), 200
    
    except Exception as e:
        app.logger.error(f"Error sending message: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
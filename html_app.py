from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
from itsdangerous import URLSafeTimedSerializer
import uuid
import os
from datetime import datetime
from utils.email_service import configure_mail, send_verification_email

app = Flask(__name__)

SECRET_KEY = "123456789ertyuicvbnm"
serializer = URLSafeTimedSerializer(SECRET_KEY)

# Path to the keys database file
keys_db_path = 'keys.json'

# Load or initialize the keys database
if not os.path.exists(keys_db_path):
    KEYS_DB = {"users": []}
    with open(keys_db_path, 'w', encoding='utf-8') as file:
        json.dump(KEYS_DB, file, ensure_ascii=False, indent=4)
else:
    with open(keys_db_path, 'r', encoding='utf-8') as file:
        KEYS_DB = json.load(file)

def save_keys_db():
    """Save the keys database to the keys.json file."""
    with open(keys_db_path, 'w', encoding='utf-8') as file:
        json.dump(KEYS_DB, file, ensure_ascii=False, indent=4)

def generate_api_key():
    """Generate a unique API key."""
    return str(uuid.uuid4())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register_user')
def register():
    return render_template('register_user.html')

@app.route('/register_user', methods=['POST'])
def register_user():
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    plan = request.form.get('plan')

    # Validate inputs
    if not username or not email or plan not in ['free', 'basic', 'premium']:
        return "Invalid input. Please fill all fields correctly.", 400
    
    # Check if email already exists
    for user in KEYS_DB["users"]:
        if user["email"] == email:
            return "Email already registered. Please use another email.", 400

    # Generate a verification token
    token = serializer.dumps(email, salt='email-verification')

    # Send verification email
    verification_url = url_for('verify_email', token=token, _external=True)
    send_verification_email(email, verification_url)

    # Save user temporarily with a token (not verified yet)
    KEYS_DB["users"].append({
        "username": username,
        "email": email,
        "plan": plan,
        "verified": False,  # User is not verified yet
        "temp_token": token  # Save token for later verification
    })

    save_keys_db()

    return "Registration initiated. Please verify your email to complete the process."

@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    try:
        # Decode the token
        email = serializer.loads(token, salt='email-verification', max_age=3600)  # 1-hour expiration
    except Exception:
        return "Invalid or expired token. Please register again.", 400

    # Mark user as verified and finalize registration
    for user in KEYS_DB["users"]:
        if user["email"] == email and user["temp_token"] == token:
            user["verified"] = True
            user.pop("temp_token", None)  # Remove token after verification

            # Assign additional details now that the user is verified
            if user["plan"] == 'free':
                user.update({
                    "member_type": 'free',
                    "api_key": generate_api_key(),
                    "usage_limit": 50,
                    "payment_status": []
                })
            elif user["plan"] == 'basic':
                user.update({
                    "member_type": 'basic',
                    "api_key": generate_api_key(),
                    "usage_limit": 1000,
                    "payment_status": [{
                        "amount": 100.00,
                        "status": "pending",
                        "date": datetime.utcnow().isoformat(),
                        "method": "online"
                    }]
                })
            else:  # Premium plan
                user.update({
                    "member_type": 'premium',
                    "api_key": generate_api_key(),
                    "usage_limit": 5000,
                    "payment_status": [{
                        "amount": 200.00,
                        "status": "pending",
                        "date": datetime.utcnow().isoformat(),
                        "method": "online"
                    }]
                })
            
            save_keys_db()
            return "Email verified successfully. You may now use the API key."
    
    return "User not found or already verified.", 400

@app.route('/verification_pending/<email>', methods=['GET'])
# This handles the email verification of the user
def verification_pending(email):
    user = next((u for u in KEYS_DB["users"] if u["email"] == email), None)
    if not user:
        return "User not found.", 404

    if user.get("email_verified"):
        # Redirect to the plan selection page once verified
        return redirect(url_for('plan_selection', email=email))

    # Serve the pending page
    return render_template('verification_pending.html', email=email)

@app.route('/api/verification_status', methods=['GET'])
# This is to verify the payment verification for access to api usage
def verification_status():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = next((user for user in KEYS_DB["users"] if user["email"] == email), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email_verified": user.get("email_verified", False),
        "payment_verified": user.get("payment_verified", False),
        "plan": user.get("plan", "free")
    })



@app.route('/plan_selection/<email>', methods=['GET', 'POST'])
# This is the route for plan and payment selection
def plan_selection(email):
    user = next((u for u in KEYS_DB["users"] if u["email"] == email), None)
    if not user:
        return "User not found.", 404

    if request.method == 'POST':
        selected_plan = request.form.get('plan')
        if selected_plan not in ['free', 'basic', 'premium']:
            return "Invalid plan selected.", 400

        user['plan'] = selected_plan
        save_keys_db()
        return "Plan selected successfully."

    return render_template('plan_selection.html', email=email)


if __name__ == '__main__':
    app.run(debug=True, port=5002)
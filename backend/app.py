from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'a_very_secret_key_that_you_should_change')

# This will act as our temporary "database"
# In a real app, this data would be stored securely in a database.
registered_users = {}
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# --- Routes to Serve the HTML Pages ---

@app.route('/')
def homepage():
    user_data = session.get('user_data', None)
    return render_template('index.html', user=user_data)

@app.route('/signup.html')
def signup_page():
    return render_template('signup.html')

@app.route('/avatar.html')
def avatar_page():
    user_data = session.get('user_data', None)
    if not user_data:
        return redirect(url_for('login_page'))
    return render_template('avatar.html', user=user_data)

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/main_menu.html')
def main_menu_page():
    user_data = session.get('user_data', None)
    if not user_data:
        return redirect(url_for('login_page'))
    return render_template('main_menu.html', user=user_data)

@app.route('/dashboard.html')
def dashboard_page():
    user_data = session.get('user_data', None)
    if not user_data:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', user=user_data)
    
@app.route('/logout')
def logout():
    session.pop('user_data', None)
    return redirect(url_for('homepage'))

# --- API Endpoints ---

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields.'}), 400
    
    if data['email'] in registered_users:
        return jsonify({'error': 'User with this email already exists.'}), 409
    
    # Store the user in our temporary database with a hashed password
    registered_users[data['email']] = {
        'username': data['username'],
        'email': data['email'],
        'password': generate_password_hash(data['password']).decode('utf-8') 
    }
    
    session['user_data'] = {
        'username': data['username'],
        'email': data['email']
    }
    
    return jsonify({'message': 'Signup successful.'}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = registered_users.get(email)
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401
    
    # If credentials are correct, store the full user object in the session
    session['user_data'] = {
        'username': user['username'],
        'email': user['email'],
        'avatar_url': user.get('avatar_url', ''),
        'preferences': user.get('preferences', [])
    }
    
    return jsonify({'message': 'Login successful.'}), 200

@app.route('/api/avatar', methods=['POST'])
def select_avatar():
    if 'user_data' not in session:
        return jsonify({'error': 'Please log in first.'}), 400
    
    data = request.get_json()
    avatar_url = data.get('avatar_url')
    if not avatar_url:
        return jsonify({'error': 'No avatar selected.'}), 400
    
    user_email = session['user_data']['email']
    user_dict = registered_users.get(user_email)
    
    if not user_dict:
        return jsonify({'error': 'Session expired. Please log in again.'}), 400

    registered_users[user_email]['avatar_url'] = avatar_url
    session['user_data']['avatar_url'] = avatar_url
    
    return jsonify({'message': 'Avatar selected.'}), 200

@app.route('/api/personalize', methods=['POST'])
def personalize():
    if 'user_data' not in session:
        return jsonify({'error': 'Please log in first.'}), 400
    
    data = request.get_json()
    preferences = data.get('preferences', {})
    
    user_email = session['user_data']['email']
    user_dict = registered_users.get(user_email)
    
    if user_dict:
        registered_users[user_email]['preferences'] = preferences
    
    session['user_data']['preferences'] = preferences
    
    return jsonify({'message': 'Registration complete.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
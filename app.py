from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simple in-memory storage
users_db = {}
# Sample user for testing
users_db['test'] = {
    'username': 'test',
    'password': 'test',  # In real app, this should be hashed
    'created_at': datetime.utcnow(),
    'emotions': {
        'happy': 2,
        'grateful': 1,
        'sad': 0,
        'angry': 0,
        'neutral': 2
    },
    'books': [
        {'title': '"Sapiens: a brief history of humankind" by Yuval Noah Harari', 'completed': True},
        {'title': '"1984" by George Orwell', 'completed': True},
        {'title': '"The Catcher in the Rye" by J.D. Salinger', 'completed': False}
    ],
    'movies': [
        {'title': 'Inception (2010)', 'completed': False},
        {'title': 'The Shawshank Redemption (1994)', 'completed': False},
        {'title': 'The Matrix (1999)', 'completed': False}
    ],
    'courses': [
        {'title': 'Harvard\'s "CS50: Introduction to Computer Science"', 'completed': False},
        {'title': 'Coursera\'s "The Science of Well Being"', 'completed': False}
    ],
    'entries': [
        {
            'emoji': '☀️',
            'title': 'Daily reflection',
            'date': 'September 10, 2024 8:57 PM',
            'content': 'Today was a productive day. I managed to complete all my tasks ahead of schedule.'
        },
        {
            'emoji': '⭐',
            'title': 'So much to be grateful for',
            'date': 'September 10, 2024 8:57 PM',
            'content': 'I am thankful for my family, friends, and the opportunities that come my way.'
        }
    ]
}

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = users_db.get(username)
        if user and user['password'] == password:
            session['username'] = username
            flash('✨ Welcome back!')
            return redirect(url_for('welcome'))
            
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))
            
        # Check if username already exists
        if username in users_db:
            flash('Username already exists')
            return redirect(url_for('register'))
            
        # Create new user
        new_user = {
            'username': username,
            'password': password,
            'created_at': datetime.utcnow(),
            'emotions': {
                'happy': 0,
                'grateful': 0,
                'sad': 0,
                'angry': 0,
                'neutral': 0
            },
            'books': [],
            'movies': [],
            'courses': [],
            'entries': []
        }
        
        users_db[username] = new_user
        flash('✨ Registration successful! Please login.')
        return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html', username=session['username'])

@app.route('/dashboard')
def dashboard():
    # Create a default user if not logged in
    if 'username' not in session:
        session['username'] = 'guest'
        if 'guest' not in users_db:
            users_db['guest'] = {
                'username': 'guest',
                'password': 'guest',
                'created_at': datetime.utcnow(),
                'emotions': {
                    'happy': 0,
                    'grateful': 0,
                    'sad': 0,
                    'angry': 0,
                    'neutral': 0
                },
                'books': [],
                'movies': [],
                'courses': [],
                'entries': []
            }
    
    user = users_db.get(session['username'])
    if not user:
        session['username'] = 'guest'
        user = users_db['guest']
        
    return render_template('dashboard.html',
                         username=session['username'],
                         emotions=user.get('emotions', {}),
                         books=user.get('books', []),
                         movies=user.get('movies', []),
                         entries=user.get('entries', []))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('👋 Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/month/<int:month>')
def month_view(month):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_db.get(session['username'])
    if not user:
        return redirect(url_for('logout'))
    
    # Filter entries for the specified month
    filtered_entries = []
    for entry in user.get('entries', []):
        entry_date = datetime.strptime(entry['date'], '%B %d, %Y %I:%M %p')
        if entry_date.month == month:
            filtered_entries.append(entry)
    
    return render_template('month.html', 
                         username=session['username'],
                         month=datetime(2024, month, 1).strftime('%B'),
                         entries=filtered_entries)

@app.route('/entry/new', methods=['GET', 'POST'])
def new_entry():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_db.get(session['username'])
    if not user:
        return redirect(url_for('logout'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        emoji = request.form.get('emoji')
        
        if not title or not content:
            flash('Title and content are required')
            return redirect(url_for('new_entry'))
        
        new_entry = {
            'emoji': emoji or '📝',
            'title': title,
            'date': datetime.now().strftime('%B %d, %Y %I:%M %p'),
            'content': content
        }
        
        user['entries'].append(new_entry)
        flash('Entry created successfully!')
        return redirect(url_for('entries'))
        
    return render_template('new_entry.html', username=session['username'])

@app.route('/entries')
def entries():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_db.get(session['username'])
    if not user:
        return redirect(url_for('logout'))
    
    # Sort entries by date (newest first)
    entries = sorted(
        user.get('entries', []),
        key=lambda x: datetime.strptime(x['date'], '%B %d, %Y %I:%M %p'),
        reverse=True
    )
    
    return render_template('entries.html', 
                         username=session['username'],
                         entries=entries)

@app.route('/entry/<date>', methods=['GET'])
def get_entry(date):
    if 'username' not in session:
        return redirect(url_for('login'))
        
    user = users_db.get(session['username'])
    if not user:
        return redirect(url_for('logout'))
    
    # Find the entry by date
    entry = next((e for e in user.get('entries', []) if e['date'] == date), None)
    if not entry:
        flash('Entry not found')
        return redirect(url_for('entries'))
    
    return render_template('entry.html', entry=entry)

@app.route('/new-entry', methods=['GET', 'POST'])
def new_entry_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = users_db.get(session['username'])
    if not user:
        flash('User not found')
        return redirect(url_for('logout'))
        
    if request.method == 'POST':
        # Handle form submission
        title = request.form.get('title')
        content = request.form.get('content')
        emoji = request.form.get('emoji')
        
        if not title or not content:
            flash('Title and content are required')
            return redirect(url_for('new_entry_page'))
        
        new_entry = {
            'emoji': emoji or '📝',
            'title': title,
            'date': datetime.now().strftime('%B %d, %Y %I:%M %p'),
            'content': content
        }
        
        # Update emotions count based on emoji
        if emoji:
            emotion_map = {
                '😊': 'happy',
                '😔': 'sad',
                '😤': 'angry',
                '🙏': 'grateful',
                '😐': 'neutral'
            }
            if emoji in emotion_map:
                emotion = emotion_map[emoji]
                user['emotions'][emotion] = user['emotions'].get(emotion, 0) + 1
        
        # Initialize entries list if it doesn't exist
        if 'entries' not in user:
            user['entries'] = []
            
        user['entries'].append(new_entry)
        flash('✨ Entry saved successfully!')
        return redirect(url_for('dashboard'))
        
    return render_template('new_entry.html', username=session['username'])

def get_emotions():
    user = users_db.get(session['username'])
    if user:
        return user['emotions']
    return {}

def get_books():
    user = users_db.get(session['username'])
    if user:
        return user['books']
    return []

def get_movies():
    user = users_db.get(session['username'])
    if user:
        return user['movies']
    return []

def get_entries():
    user = users_db.get(session['username'])
    if user:
        return user['entries']
    return []

@app.route('/debug/database')
def view_database():
    if app.debug:  # Only allow in debug mode
        return {
            'users': {
                username: {
                    'username': user['username'],
                    'created_at': user['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'emotions': user['emotions'],
                    'entries_count': len(user.get('entries', [])),
                    'entries': user.get('entries', [])
                }
                for username, user in users_db.items()
            }
        }
    return {'error': 'Debug mode not enabled'}, 403

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 
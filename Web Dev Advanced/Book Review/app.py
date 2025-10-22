import os
import sys
import json
import hashlib
import secrets
from datetime import datetime
from functools import wraps

# Django Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '__main__')

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.urls import path
from django.db import connection

# Configure Django Settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='your-secret-key-change-in-production',
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=['*'],
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'bookreviews.db',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
        ],
    )
    application = get_wsgi_application()

# Database helper functions
def init_db():
    """Initialize database tables"""
    with connection.cursor() as cursor:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                review_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

# Utility functions
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

def get_json_body(request):
    """Parse JSON from request body"""
    try:
        return json.loads(request.body.decode('utf-8'))
    except:
        return {}

def cors_headers(response):
    """Add CORS headers to response"""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Authentication decorator
def require_auth(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return cors_headers(JsonResponse({'error': 'Unauthorized'}, status=401))
        
        token = auth_header.split(' ')[1]
        
        with connection.cursor() as cursor:
            cursor.execute('SELECT user_id FROM tokens WHERE token = ?', [token])
            row = cursor.fetchone()
            
            if not row:
                return cors_headers(JsonResponse({'error': 'Invalid token'}, status=401))
            
            request.user_id = row[0]
        
        return view_func(request, *args, **kwargs)
    return wrapper

# API Views
@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register(request):
    """Register a new user"""
    if request.method == "OPTIONS":
        return cors_headers(JsonResponse({}))
    
    data = get_json_body(request)
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not email or not password:
        return cors_headers(JsonResponse({'error': 'All fields required'}, status=400))
    
    password_hash = hash_password(password)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                [username, email, password_hash]
            )
        return cors_headers(JsonResponse({'message': 'User registered successfully'}))
    except:
        return cors_headers(JsonResponse({'error': 'Username or email already exists'}, status=400))

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login(request):
    """Login user and return token"""
    if request.method == "OPTIONS":
        return cors_headers(JsonResponse({}))
    
    data = get_json_body(request)
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return cors_headers(JsonResponse({'error': 'Email and password required'}, status=400))
    
    password_hash = hash_password(password)
    
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT id, username, email FROM users WHERE email = ? AND password_hash = ?',
            [email, password_hash]
        )
        user = cursor.fetchone()
        
        if not user:
            return cors_headers(JsonResponse({'error': 'Invalid credentials'}, status=401))
        
        token = generate_token()
        cursor.execute('INSERT INTO tokens (user_id, token) VALUES (?, ?)', [user[0], token])
        
        return cors_headers(JsonResponse({
            'token': token,
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        }))

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
@require_auth
def reviews_list(request):
    """Get all reviews or create new review"""
    if request.method == "OPTIONS":
        return cors_headers(JsonResponse({}))
    
    if request.method == "GET":
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT r.id, r.user_id, r.title, r.author, r.rating, r.review_text, 
                       r.created_at, u.username
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                ORDER BY r.created_at DESC
            ''')
            reviews = []
            for row in cursor.fetchall():
                reviews.append({
                    'id': row[0],
                    'user_id': row[1],
                    'title': row[2],
                    'author': row[3],
                    'rating': row[4],
                    'review_text': row[5],
                    'created_at': row[6],
                    'username': row[7]
                })
            return cors_headers(JsonResponse(reviews, safe=False))
    
    elif request.method == "POST":
        data = get_json_body(request)
        title = data.get('title', '').strip()
        author = data.get('author', '').strip()
        rating = data.get('rating')
        review_text = data.get('review_text', '').strip()
        
        if not title or not author or not rating or not review_text:
            return cors_headers(JsonResponse({'error': 'All fields required'}, status=400))
        
        if not (1 <= rating <= 5):
            return cors_headers(JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400))
        
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO reviews (user_id, title, author, rating, review_text)
                VALUES (?, ?, ?, ?, ?)
            ''', [request.user_id, title, author, rating, review_text])
            
            review_id = cursor.lastrowid
            
            cursor.execute('''
                SELECT r.id, r.user_id, r.title, r.author, r.rating, r.review_text, 
                       r.created_at, u.username
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.id = ?
            ''', [review_id])
            
            row = cursor.fetchone()
            review = {
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'author': row[3],
                'rating': row[4],
                'review_text': row[5],
                'created_at': row[6],
                'username': row[7]
            }
            
            return cors_headers(JsonResponse(review, status=201))

@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
@require_auth
def user_reviews(request, user_id):
    """Get reviews by specific user"""
    if request.method == "OPTIONS":
        return cors_headers(JsonResponse({}))
    
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT r.id, r.user_id, r.title, r.author, r.rating, r.review_text, 
                   r.created_at, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
        ''', [user_id])
        
        reviews = []
        for row in cursor.fetchall():
            reviews.append({
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'author': row[3],
                'rating': row[4],
                'review_text': row[5],
                'created_at': row[6],
                'username': row[7]
            })
        
        return cors_headers(JsonResponse(reviews, safe=False))

@csrf_exempt
@require_http_methods(["PUT", "DELETE", "OPTIONS"])
@require_auth
def review_detail(request, review_id):
    """Update or delete a review"""
    if request.method == "OPTIONS":
        return cors_headers(JsonResponse({}))
    
    with connection.cursor() as cursor:
        # Check if review exists and belongs to user
        cursor.execute('SELECT user_id FROM reviews WHERE id = ?', [review_id])
        row = cursor.fetchone()
        
        if not row:
            return cors_headers(JsonResponse({'error': 'Review not found'}, status=404))
        
        if row[0] != request.user_id:
            return cors_headers(JsonResponse({'error': 'Unauthorized'}, status=403))
        
        if request.method == "PUT":
            data = get_json_body(request)
            review_text = data.get('review_text', '').strip()
            
            if not review_text:
                return cors_headers(JsonResponse({'error': 'Review text required'}, status=400))
            
            cursor.execute('''
                UPDATE reviews 
                SET review_text = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', [review_text, review_id])
            
            return cors_headers(JsonResponse({'message': 'Review updated successfully'}))
        
        elif request.method == "DELETE":
            cursor.execute('DELETE FROM reviews WHERE id = ?', [review_id])
            return cors_headers(JsonResponse({'message': 'Review deleted successfully'}))

# URL Configuration
urlpatterns = [
    path('api/register/', register),
    path('api/login/', login),
    path('api/reviews/', reviews_list),
    path('api/reviews/user/<int:user_id>/', user_reviews),
    path('api/reviews/<int:review_id>/', review_detail),
]

# Initialize database on startup
init_db()

if __name__ == '__main__':
    # Run development server
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0], 'runserver', '0.0.0.0:8000'])
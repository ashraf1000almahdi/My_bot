import os
import logging
from datetime import datetime
from functools import wraps
from flask import request, jsonify

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds):
    """Format duration in human readable format"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def validate_telegram_id(telegram_id):
    """Validate Telegram ID format"""
    try:
        tid = int(telegram_id)
        return tid > 0 and tid < 10**10  # Reasonable range for Telegram IDs
    except (ValueError, TypeError):
        return False

def log_user_action(user_id, action, details=None):
    """Log user actions for monitoring"""
    timestamp = datetime.utcnow().isoformat()
    log_message = f"User {user_id} performed {action}"
    
    if details:
        log_message += f" - {details}"
    
    logging.info(log_message)

def rate_limit(max_calls=10, window_seconds=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting implementation
            # In production, use Redis or similar
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def clean_filename(filename):
    """Clean filename for safe file operations"""
    import re
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip()
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:100-len(ext)] + ext
    
    return filename

def is_valid_url(url):
    """Check if URL is valid"""
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_platform_from_url(url):
    """Extract platform name from URL"""
    from urllib.parse import urlparse
    
    domain_to_platform = {
        'youtube.com': 'YouTube',
        'youtu.be': 'YouTube',
        'instagram.com': 'Instagram',
        'tiktok.com': 'TikTok',
        'twitter.com': 'Twitter',
        'x.com': 'Twitter',
        'facebook.com': 'Facebook',
        'vimeo.com': 'Vimeo',
        'dailymotion.com': 'Dailymotion'
    }
    
    try:
        domain = urlparse(url).netloc.lower()
        for key, platform in domain_to_platform.items():
            if key in domain:
                return platform
        return 'Unknown'
    except:
        return 'Unknown'

def create_error_response(message, status_code=400):
    """Create standardized error response"""
    return jsonify({
        'error': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }), status_code

def create_success_response(data=None, message="Success"):
    """Create standardized success response"""
    response = {
        'error': False,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if data:
        response['data'] = data
    
    return jsonify(response)

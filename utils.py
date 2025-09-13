from datetime import datetime
import re

# Centralized category list for consistency across the application
CATEGORY_OPTIONS = [
    "Potholes", 
    "Garbage", 
    "Street Lights", 
    "Water Supply", 
    "Drainage", 
    "Traffic Signs", 
    "Other"
]

def get_category_color(category):
    """Return a color for map markers based on issue category"""
    # Using only valid Folium colors: red, blue, green, purple, orange, darkred, lightred, beige, darkblue, darkgreen, cadetblue, darkpurple, white, pink, lightblue, lightgreen, gray, black, lightgray
    color_map = {
        'Potholes': 'red',
        'Garbage': 'orange', 
        'Street Lights': 'lightblue',  # Fixed: yellow is not valid Folium color
        'Water Supply': 'blue',
        'Drainage': 'purple',
        'Traffic Signs': 'green',
        'Other': 'gray'
    }
    return color_map.get(category, 'gray')

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        # Parse the timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return timestamp_str

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Simple validation for phone numbers
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return re.match(pattern, phone.replace(' ', '').replace('-', '')) is not None

def sanitize_input(text):
    """Comprehensive input sanitization for HTML contexts"""
    if not text:
        return ""
    
    # Escape all HTML-sensitive characters including ampersands
    text = text.replace('&', '&amp;')  # Must be first to avoid double-encoding
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#x27;')
    
    return text.strip()

def get_status_emoji(status):
    """Get emoji for issue status"""
    emoji_map = {
        'pending': '🟡',
        'in_progress': '🔵', 
        'resolved': '🟢'
    }
    return emoji_map.get(status, '⚪')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def truncate_text(text, max_length=100):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def get_priority_level(category, days_old):
    """Determine priority level based on category and age"""
    high_priority_categories = ['Water Supply', 'Street Lights', 'Drainage']
    
    if category in high_priority_categories:
        if days_old > 7:
            return 'Critical'
        elif days_old > 3:
            return 'High'
        else:
            return 'Medium'
    else:
        if days_old > 14:
            return 'High'
        elif days_old > 7:
            return 'Medium'
        else:
            return 'Low'

def generate_report_summary(issues):
    """Generate a summary report of issues"""
    if not issues:
        return "No issues to report."
    
    total = len(issues)
    by_status = {}
    by_category = {}
    
    for issue in issues:
        # Count by status
        status = issue['status']
        by_status[status] = by_status.get(status, 0) + 1
        
        # Count by category
        category = issue['category']
        by_category[category] = by_category.get(category, 0) + 1
    
    summary = f"Total Issues: {total}\n"
    summary += "\nBy Status:\n"
    for status, count in by_status.items():
        summary += f"  {status.title()}: {count}\n"
    
    summary += "\nBy Category:\n"
    for category, count in by_category.items():
        summary += f"  {category}: {count}\n"
    
    return summary

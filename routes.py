from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import User, Download, BotStats
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

@app.route('/')
def dashboard():
    """Main dashboard"""
    with app.app_context():
        # Update stats
        stats = BotStats.get_stats()
        stats.update_stats()
        
        # Get recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        recent_downloads = Download.query.order_by(Download.created_at.desc()).limit(10).all()
        
        # Get daily stats for the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        daily_stats = db.session.query(
            func.date(Download.created_at).label('date'),
            func.count(Download.id).label('downloads')
        ).filter(
            Download.created_at >= seven_days_ago
        ).group_by(
            func.date(Download.created_at)
        ).all()
        
        return render_template('dashboard.html', 
                             stats=stats,
                             recent_users=recent_users,
                             recent_downloads=recent_downloads,
                             daily_stats=daily_stats)

@app.route('/users')
def users():
    """Users management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('users.html', users=users)

@app.route('/downloads')
def downloads():
    """Downloads management page"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    per_page = 20
    
    query = Download.query
    if status != 'all':
        query = query.filter_by(status=status)
    
    downloads = query.order_by(Download.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('downloads.html', downloads=downloads, current_status=status)

@app.route('/api/stats')
def api_stats():
    """API endpoint for real-time stats"""
    stats = BotStats.get_stats()
    stats.update_stats()
    
    return jsonify({
        'total_users': stats.total_users,
        'total_downloads': stats.total_downloads,
        'successful_downloads': stats.successful_downloads,
        'failed_downloads': stats.failed_downloads,
        'success_rate': round((stats.successful_downloads / max(stats.total_downloads, 1)) * 100, 2)
    })

@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    """API endpoint for user details"""
    user = User.query.get_or_404(user_id)
    
    # Get user's download stats
    total_downloads = Download.query.filter_by(user_id=user.id).count()
    successful_downloads = Download.query.filter_by(user_id=user.id, status='completed').count()
    failed_downloads = Download.query.filter_by(user_id=user.id, status='failed').count()
    
    return jsonify({
        'id': user.id,
        'telegram_id': user.telegram_id,
        'display_name': user.display_name,
        'username': user.username,
        'is_subscribed': user.is_subscribed,
        'created_at': user.created_at.isoformat(),
        'total_downloads': total_downloads,
        'successful_downloads': successful_downloads,
        'failed_downloads': failed_downloads
    })

@app.route('/api/download/<int:download_id>')
def api_download(download_id):
    """API endpoint for download details"""
    download = Download.query.get_or_404(download_id)
    
    return jsonify({
        'id': download.id,
        'url': download.url,
        'title': download.title,
        'platform': download.platform,
        'status': download.status,
        'format_requested': download.format_requested,
        'quality_requested': download.quality_requested,
        'file_size': download.file_size,
        'error_message': download.error_message,
        'created_at': download.created_at.isoformat(),
        'completed_at': download.completed_at.isoformat() if download.completed_at else None,
        'user': {
            'id': download.user.id,
            'display_name': download.user.display_name,
            'telegram_id': download.user.telegram_id
        }
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

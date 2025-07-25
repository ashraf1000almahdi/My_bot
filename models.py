from app import db
from datetime import datetime
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription_checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    downloads = db.relationship('Download', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username or self.telegram_id}>'
    
    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.telegram_id}"

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(200), nullable=True)
    platform = db.Column(db.String(50), nullable=True)
    format_requested = db.Column(db.String(10), nullable=True)
    quality_requested = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    file_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.BigInteger, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Download {self.id}: {self.title or self.url}>'

class BotStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_users = db.Column(db.Integer, default=0)
    total_downloads = db.Column(db.Integer, default=0)
    successful_downloads = db.Column(db.Integer, default=0)
    failed_downloads = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @classmethod
    def get_stats(cls):
        stats = cls.query.first()
        if not stats:
            stats = cls()
            db.session.add(stats)
            db.session.commit()
        return stats
    
    def update_stats(self):
        self.total_users = User.query.count()
        self.total_downloads = Download.query.count()
        self.successful_downloads = Download.query.filter_by(status='completed').count()
        self.failed_downloads = Download.query.filter_by(status='failed').count()
        self.updated_at = datetime.utcnow()
        db.session.commit()

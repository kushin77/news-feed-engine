"""
Gamification Engine - Main Flask Application

Microservice for managing points, badges, and leaderboards.
"""
import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==================== Models ====================

class User(db.Model):
    """User model for gamification"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    points = db.Column(db.BigInteger, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    badges = db.relationship('UserBadge', back_populates='user', lazy='dynamic')
    transactions = db.relationship('PointTransaction', back_populates='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'points': self.points,
            'badges': [ub.badge.to_dict() for ub in self.badges],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Badge(db.Model):
    """Badge definitions"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.Text)
    points = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('UserBadge', back_populates='badge', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'points': self.points,
            'icon': self.icon
        }


class UserBadge(db.Model):
    """User-Badge association"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='badges')
    badge = db.relationship('Badge', back_populates='users')
    
    def to_dict(self):
        return {
            'badge': self.badge.to_dict(),
            'awarded_at': self.awarded_at.isoformat() if self.awarded_at else None
        }


class PointTransaction(db.Model):
    """Point transaction history"""
    __tablename__ = 'point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='transactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'points': self.points,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== Routes ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gamification-engine',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'service': 'gamification-engine',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'award_points': 'POST /api/points',
            'leaderboard': 'GET /api/leaderboard',
            'award_badge': 'POST /api/badges',
            'get_user': 'GET /api/users/<user_id>'
        }
    })


@app.route('/api/points', methods=['POST'])
def award_points():
    """Award points to a user"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'points' not in data:
        return jsonify({'error': 'user_id and points are required'}), 400
    
    user_id = data['user_id']
    points = data['points']
    reason = data.get('reason', 'Points awarded')
    
    # Find or create user
    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id, username=data.get('username', f'user_{user_id[:8]}'))
        db.session.add(user)
    
    # Update points
    user.points += points
    
    # Record transaction
    transaction = PointTransaction(user_id=user_id, points=points, reason=reason)
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'new_points': user.points,
        'transaction': transaction.to_dict()
    })


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard of top users"""
    limit = request.args.get('limit', 10, type=int)
    
    users = User.query.order_by(User.points.desc()).limit(limit).all()
    
    return jsonify({
        'leaderboard': [
            {
                'rank': idx + 1,
                'user_id': user.id,
                'username': user.username,
                'points': user.points,
                'badge_count': user.badges.count()
            }
            for idx, user in enumerate(users)
        ]
    })


@app.route('/api/badges', methods=['POST'])
def award_badge():
    """Award a badge to a user"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'badge_name' not in data:
        return jsonify({'error': 'user_id and badge_name are required'}), 400
    
    user_id = data['user_id']
    badge_name = data['badge_name']
    
    # Find user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find badge
    badge = Badge.query.filter_by(name=badge_name).first()
    if not badge:
        return jsonify({'error': 'Badge not found'}), 404
    
    # Check if user already has badge
    existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first()
    if existing:
        return jsonify({'error': 'User already has this badge'}), 400
    
    # Award badge
    user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
    db.session.add(user_badge)
    
    # Award bonus points for badge
    user.points += badge.points
    transaction = PointTransaction(
        user_id=user_id, 
        points=badge.points, 
        reason=f'Badge awarded: {badge_name}'
    )
    db.session.add(transaction)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'badge': badge.to_dict(),
        'new_points': user.points
    })


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile with points and badges"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())


# ==================== Database Seeding ====================

def seed_default_badges():
    """Create default badges if they don't exist"""
    default_badges = [
        {'name': 'First Post', 'description': 'Created your first post', 'points': 10},
        {'name': 'Early Adopter', 'description': 'Joined during beta', 'points': 100},
        {'name': 'Viral Hit', 'description': 'Got 10,000 views on a post', 'points': 500},
        {'name': 'Community Builder', 'description': 'Gained 100 followers', 'points': 250},
        {'name': 'Top Creator', 'description': 'Reached 1,000 followers', 'points': 1000},
        {'name': 'Engagement Master', 'description': '100 likes on a single post', 'points': 150},
        {'name': 'Streak Champion', 'description': 'Posted for 7 days in a row', 'points': 200},
        {'name': 'Trendsetter', 'description': 'Created content that started a trend', 'points': 300},
    ]
    
    for badge_data in default_badges:
        existing = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()


# ==================== Main ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_badges()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

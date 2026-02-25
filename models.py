from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    stories = db.relationship('Story', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Story(db.Model):
    """小说模型"""
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)  # AI生成，可能没有标题
    outline = db.Column(db.Text, nullable=False)  # 用户输入的大纲
    genre = db.Column(db.String(50), nullable=False)  # 小说类型
    word_count = db.Column(db.Integer, nullable=False)  # 字数
    content = db.Column(db.Text, nullable=False)  # AI生成的内容
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'outline': self.outline,
            'genre': self.genre,
            'word_count': self.word_count,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

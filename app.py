import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Story
import requests

app = Flask(__name__, static_folder='static')
CORS(app, supports_credentials=True)

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ainovel.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400 * 7  # 7天有效期

# 初始化
db.init_app(app)
jwt = JWTManager(app)

# DeepSeek API 配置
DEEPSEEK_API_KEY = 'sk-075ee6f2364c45b1a8b1e70408bda698'
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# 小说类型提示词映射
GENRE_PROMPTS = {
    'scifi': '科幻风格，包含未来科技、太空探索、人工智能等元素',
    'cultivation': '修仙风格，包含修炼体系、灵气复苏、宗门争斗等元素',
    'apocalypse': '末世风格，包含灾难求生、变异生物、资源匮乏等元素',
    'urban': '都市风格，包含职场生活、情感纠葛、社会现实等元素',
    'mystery': '悬疑风格，包含层层迷雾、惊人真相、紧张推理等元素',
    'fantasy': '奇幻风格，包含魔法世界、异族生物、史诗冒险等元素',
    'wuxia': '武侠风格，包含江湖恩怨、绝世武功、侠义精神等元素',
    'romance': '浪漫风格，包含甜蜜爱情、情感纠葛、幸福结局等元素',
    'historical': '历史风格，包含古代背景、真实历史人物、风云变幻等元素'
}

GENRE_NAMES = {
    'scifi': '科幻', 'cultivation': '修仙', 'apocalypse': '末世',
    'urban': '都市', 'mystery': '悬疑', 'fantasy': '奇幻',
    'wuxia': '武侠', 'romance': '浪漫', 'historical': '历史'
}

# ===== 静态文件 =====
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory('static', 'login.html')

@app.route('/register')
def register_page():
    return send_from_directory('static', 'register.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# ===== 用户认证 =====
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # 验证
    if not username or not email or not password:
        return jsonify({'error': '请填写所有字段'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少6位'}), 400
    
    # 检查用户是否存在
    if User.query.filter((User.username==username) | (User.email==email)).first():
        return jsonify({'error': '用户名或邮箱已存在'}), 400
    
    # 创建用户
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    # 生成token
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': user.to_dict()
    })

@app.route('/api/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': user.to_dict()})

# ===== 小说生成 =====
@app.route('/api/generate', methods=['POST'])
@jwt_required()
def generate_story():
    user_id = get_jwt_identity()
    data = request.json
    outline = data.get('outline', '')
    genre = data.get('genre', 'scifi')
    word_count = int(data.get('wordCount', 5000))

    if not outline:
        return jsonify({'error': '请输入故事大纲'}), 400

    # 构建提示词
    genre_prompt = GENRE_PROMPTS.get(genre, GENRE_PROMPTS['scifi'])
    genre_name = GENRE_NAMES.get(genre, '科幻')
    
    system_prompt = f"""你是一位专业的小说作家，擅长创作各种类型的故事。
请根据用户提供的故事大纲，创作一篇{word_count}字左右的{genre_name}小说。

风格要求：{genre_prompt}

注意事项：
1. 故事情节要完整，有开头、发展、高潮、结尾
2. 人物性格鲜明，有血有肉
3. 描写细腻生动，环境、人物、心理都要到位
4. 对话自然流畅，符合人物身份
5. 根据故事类型，使用相应的专业术语和氛围描写
6. 字数要接近目标字数{word_count}字

请直接输出小说内容，不需要任何前缀或说明。"""

    user_prompt = f"故事大纲：{outline}"

    try:
        # 调用 DeepSeek API
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.8,
            'max_tokens': 8192
        }

        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=120
        )

        if response.status_code != 200:
            return jsonify({'error': f'API调用失败: {response.text}'}), 500

        result = response.json()
        story_content = result['choices'][0]['message']['content']

        # 保存到数据库
        story = Story(
            user_id=user_id,
            outline=outline,
            genre=genre_name,
            word_count=len(story_content),
            content=story_content
        )
        db.session.add(story)
        db.session.commit()

        return jsonify({
            'success': True,
            'story': story_content,
            'genre': genre_name,
            'word_count': len(story_content),
            'story_id': story.id
        })

    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时，请稍后重试'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== 用户故事记录 =====
@app.route('/api/stories', methods=['GET'])
@jwt_required()
def get_stories():
    user_id = get_jwt_identity()
    stories = Story.query.filter_by(user_id=user_id).order_by(Story.created_at.desc()).all()
    return jsonify({'stories': [s.to_dict() for s in stories]})

@app.route('/api/stories/<int:story_id>', methods=['GET'])
@jwt_required()
def get_story(story_id):
    user_id = get_jwt_identity()
    story = Story.query.filter_by(id=story_id, user_id=user_id).first()
    if not story:
        return jsonify({'error': '故事不存在'}), 404
    return jsonify({'story': story.to_dict()})

# ===== 健康检查 =====
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# ===== 初始化数据库 =====
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

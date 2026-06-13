from flask import Blueprint, request, jsonify
from models import db, User
from utils.auth import hash_password, verify_password, generate_jwt, login_required, get_current_user_id

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    nickname = (data.get('nickname') or '').strip()

    if not email or not password:
        return jsonify({'code': 400, 'message': '邮箱和密码不能为空'})
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码至少6位'})
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册'})

    user = User(
        email=email,
        password=hash_password(password),
        nickname=nickname or '学习者'
    )
    db.session.add(user)
    db.session.commit()

    token = generate_jwt(user.id, user.email)
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nickname': user.nickname,
                'daily_goal': user.daily_goal,
                'study_mode': user.study_mode
            }
        }
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'code': 400, 'message': '用户不存在'})
    if not verify_password(password, user.password):
        return jsonify({'code': 400, 'message': '密码错误'})

    token = generate_jwt(user.id, user.email)
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nickname': user.nickname,
                'daily_goal': user.daily_goal,
                'study_mode': user.study_mode
            }
        }
    })

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'})

    from models import UserWord, DailyRecord
    from datetime import datetime, timedelta
    from sqlalchemy import func

    total_words = UserWord.query.filter_by(user_id=user_id).count()
    mastered_words = UserWord.query.filter_by(user_id=user_id, status='mastered').count()
    learning_words = UserWord.query.filter_by(user_id=user_id, status='learning').count()
    study_days = DailyRecord.query.filter_by(user_id=user_id).count()

    today = datetime.now().date()
    today_record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()
    today_new = today_record.new_count if today_record else 0
    today_review = today_record.review_count if today_record else 0
    today_total = today_record.total_count if today_record else 0

    streak = 0
    d = today
    while True:
        r = DailyRecord.query.filter_by(user_id=user_id, date=d).first()
        if r and r.total_count > 0:
            streak += 1
            d = d - timedelta(days=1)
        else:
            break

    return jsonify({
        'code': 200,
        'data': {
            'user': {
                'id': user.id,
                'email': user.email,
                'nickname': user.nickname,
                'daily_goal': user.daily_goal,
                'study_mode': user.study_mode,
                'created_at': user.created_at.strftime('%Y-%m-%d')
            },
            'stats': {
                'total_words': total_words,
                'mastered_words': mastered_words,
                'learning_words': learning_words,
                'study_days': study_days,
                'streak': streak,
                'today_new': today_new,
                'today_review': today_review,
                'today_total': today_total
            }
        }
    })

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'})

    data = request.get_json()
    if 'nickname' in data:
        user.nickname = data['nickname'].strip() or user.nickname
    if 'daily_goal' in data:
        goal = int(data['daily_goal'])
        if goal in [10, 20, 50]:
            user.daily_goal = goal
        else:
            return jsonify({'code': 400, 'message': '每日目标只能是10/20/50'})
    if 'study_mode' in data:
        mode = data['study_mode']
        if mode in ['card', 'spelling']:
            user.study_mode = mode
        else:
            return jsonify({'code': 400, 'message': '学习模式只能是card/spelling'})
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return jsonify({'code': 400, 'message': '密码至少6位'})
        user.password = hash_password(data['password'])

    db.session.commit()
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'id': user.id,
            'nickname': user.nickname,
            'daily_goal': user.daily_goal,
            'study_mode': user.study_mode
        }
    })

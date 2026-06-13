from flask import Blueprint, request, jsonify
from models import db, Word, UserWord
from utils.auth import login_required, get_current_user_id
from sqlalchemy import or_

word_bp = Blueprint('word', __name__)

def serialize_word(w, user_word=None):
    data = {
        'id': w.id,
        'word': w.word,
        'phonetic': w.phonetic or '',
        'meaning': w.meaning,
        'example': w.example or '',
        'example_trans': w.example_trans or ''
    }
    if user_word:
        data['user_word_id'] = user_word.id
        data['status'] = user_word.status
        data['ease_factor'] = user_word.ease_factor
        data['interval'] = user_word.interval
        data['repetitions'] = user_word.repetitions
        data['next_review'] = user_word.next_review.strftime('%Y-%m-%d') if user_word.next_review else None
        data['total_reviews'] = user_word.total_reviews
        data['correct_count'] = user_word.correct_count
    return data

@word_bp.route('/search', methods=['GET'])
@login_required
def search_word():
    keyword = (request.args.get('keyword') or '').strip()
    if not keyword:
        return jsonify({'code': 400, 'message': '搜索关键词不能为空'})

    user_id = get_current_user_id()
    words = Word.query.filter(
        or_(
            Word.word.like(f'%{keyword}%'),
            Word.meaning.like(f'%{keyword}%')
        )
    ).limit(50).all()

    result = []
    for w in words:
        uw = UserWord.query.filter_by(user_id=user_id, word_id=w.id).first()
        result.append(serialize_word(w, uw))

    return jsonify({
        'code': 200,
        'data': result
    })

@word_bp.route('/<int:word_id>', methods=['GET'])
@login_required
def get_word(word_id):
    user_id = get_current_user_id()
    w = Word.query.get(word_id)
    if not w:
        return jsonify({'code': 404, 'message': '单词不存在'})
    uw = UserWord.query.filter_by(user_id=user_id, word_id=w.id).first()
    return jsonify({
        'code': 200,
        'data': serialize_word(w, uw)
    })

@word_bp.route('/add-custom', methods=['POST'])
@login_required
def add_custom_word():
    user_id = get_current_user_id()
    data = request.get_json()
    word_text = (data.get('word') or '').strip()
    meaning = (data.get('meaning') or '').strip()
    phonetic = (data.get('phonetic') or '').strip()
    example = (data.get('example') or '').strip()
    example_trans = (data.get('example_trans') or '').strip()

    if not word_text or not meaning:
        return jsonify({'code': 400, 'message': '单词和释义不能为空'})

    existing = Word.query.filter_by(word=word_text).first()
    if existing:
        uw = UserWord.query.filter_by(user_id=user_id, word_id=existing.id).first()
        if uw:
            return jsonify({'code': 400, 'message': '该单词已在您的生词本中'})
        uw = UserWord(user_id=user_id, word_id=existing.id, is_custom=True)
        db.session.add(uw)
        db.session.commit()
        return jsonify({'code': 200, 'message': '添加成功', 'data': serialize_word(existing, uw)})

    w = Word(word=word_text, phonetic=phonetic, meaning=meaning, example=example, example_trans=example_trans)
    db.session.add(w)
    db.session.flush()
    uw = UserWord(user_id=user_id, word_id=w.id, is_custom=True)
    db.session.add(uw)
    db.session.commit()
    return jsonify({'code': 200, 'message': '添加成功', 'data': serialize_word(w, uw)})

@word_bp.route('/custom-list', methods=['GET'])
@login_required
def custom_list():
    user_id = get_current_user_id()
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    offset = (page - 1) * size

    query = UserWord.query.filter_by(user_id=user_id, is_custom=True)
    total = query.count()
    user_words = query.order_by(UserWord.created_at.desc()).offset(offset).limit(size).all()

    result = []
    for uw in user_words:
        result.append(serialize_word(uw.word, uw))

    return jsonify({
        'code': 200,
        'data': {
            'list': result,
            'total': total,
            'page': page,
            'size': size
        }
    })

@word_bp.route('/custom/<int:user_word_id>', methods=['DELETE'])
@login_required
def delete_custom(user_word_id):
    user_id = get_current_user_id()
    uw = UserWord.query.filter_by(id=user_word_id, user_id=user_id, is_custom=True).first()
    if not uw:
        return jsonify({'code': 404, 'message': '记录不存在'})
    db.session.delete(uw)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'})

from flask import Blueprint, request, jsonify
from models import db, VocabBook, VocabWord, Word, UserVocabBook, UserWord
from utils.auth import login_required, get_current_user_id
from sqlalchemy import func

vocab_bp = Blueprint('vocab', __name__)

@vocab_bp.route('/list', methods=['GET'])
@login_required
def list_books():
    user_id = get_current_user_id()
    preset_books = VocabBook.query.filter_by(is_preset=True).all()
    custom_books = VocabBook.query.filter_by(is_preset=False).all()

    active_ids = set()
    uvbs = UserVocabBook.query.filter_by(user_id=user_id, is_active=True).all()
    active_ids = set(uvb.vocab_book_id for uvb in uvbs)

    def serialize_book(b):
        word_count = VocabWord.query.filter_by(vocab_book_id=b.id).count()
        user_words = UserWord.query.filter_by(user_id=user_id, vocab_book_id=b.id).count() if b.is_preset else 0
        return {
            'id': b.id,
            'name': b.name,
            'description': b.description or '',
            'is_preset': b.is_preset,
            'word_count': word_count,
            'learned_count': user_words,
            'is_active': b.id in active_ids,
            'created_at': b.created_at.strftime('%Y-%m-%d') if b.created_at else ''
        }

    return jsonify({
        'code': 200,
        'data': {
            'preset': [serialize_book(b) for b in preset_books],
            'custom': [serialize_book(b) for b in custom_books]
        }
    })

@vocab_bp.route('/<int:book_id>/activate', methods=['POST'])
@login_required
def activate_book(book_id):
    user_id = get_current_user_id()
    book = VocabBook.query.get(book_id)
    if not book:
        return jsonify({'code': 404, 'message': '词库不存在'})

    data = request.get_json() or {}
    active = data.get('active', True)

    uvb = UserVocabBook.query.filter_by(user_id=user_id, vocab_book_id=book_id).first()
    if uvb:
        uvb.is_active = active
    else:
        uvb = UserVocabBook(user_id=user_id, vocab_book_id=book_id, is_active=active)
        db.session.add(uvb)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '操作成功',
        'data': {'book_id': book_id, 'is_active': active}
    })

@vocab_bp.route('/<int:book_id>/words', methods=['GET'])
@login_required
def book_words(book_id):
    user_id = get_current_user_id()
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 20))
    keyword = (request.args.get('keyword') or '').strip()
    offset = (page - 1) * size

    query = VocabWord.query.filter_by(vocab_book_id=book_id)
    if keyword:
        word_ids = [w.id for w in Word.query.filter(
            (Word.word.like(f'%{keyword}%')) | (Word.meaning.like(f'%{keyword}%'))
        ).all()]
        query = query.filter(VocabWord.word_id.in_(word_ids)) if word_ids else query.filter(VocabWord.id == -1)

    total = query.count()
    vws = query.order_by(VocabWord.id.asc()).offset(offset).limit(size).all()

    user_word_ids = {}
    if vws:
        wids = [vw.word_id for vw in vws]
        uws = UserWord.query.filter(UserWord.user_id == user_id, UserWord.word_id.in_(wids)).all()
        for uw in uws:
            user_word_ids[uw.word_id] = uw

    result = []
    for vw in vws:
        w = vw.word
        uw = user_word_ids.get(w.id)
        item = {
            'word_id': w.id,
            'word': w.word,
            'phonetic': w.phonetic or '',
            'meaning': w.meaning,
            'example': w.example or '',
            'example_trans': w.example_trans or ''
        }
        if uw:
            item['learned'] = True
            item['status'] = uw.status
            item['next_review'] = uw.next_review.strftime('%Y-%m-%d') if uw.next_review else None
        else:
            item['learned'] = False
        result.append(item)

    return jsonify({
        'code': 200,
        'data': {
            'list': result,
            'total': total,
            'page': page,
            'size': size
        }
    })

@vocab_bp.route('/custom', methods=['POST'])
@login_required
def create_custom_book():
    user_id = get_current_user_id()
    data = request.get_json()
    name = (data.get('name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name:
        return jsonify({'code': 400, 'message': '词库名称不能为空'})

    book = VocabBook(name=name, description=description, is_preset=False)
    db.session.add(book)
    db.session.flush()

    uvb = UserVocabBook(user_id=user_id, vocab_book_id=book.id, is_active=True)
    db.session.add(uvb)
    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '创建成功',
        'data': {
            'id': book.id,
            'name': book.name,
            'description': book.description
        }
    })

@vocab_bp.route('/<int:book_id>', methods=['DELETE'])
@login_required
def delete_book(book_id):
    user_id = get_current_user_id()
    book = VocabBook.query.filter_by(id=book_id, is_preset=False).first()
    if not book:
        return jsonify({'code': 404, 'message': '自定义词库不存在'})

    VocabWord.query.filter_by(vocab_book_id=book_id).delete()
    UserVocabBook.query.filter_by(vocab_book_id=book_id).delete()
    UserWord.query.filter_by(vocab_book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()

    return jsonify({'code': 200, 'message': '删除成功'})

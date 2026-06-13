from flask import Blueprint, request, jsonify
from models import db, User, Word, UserWord, VocabBook, VocabWord, UserVocabBook, DailyRecord
from utils.auth import login_required, get_current_user_id
from utils.sm2 import SM2Algorithm
from datetime import datetime, date
from sqlalchemy import and_

study_bp = Blueprint('study', __name__)

def serialize_word_learning(uw):
    w = uw.word
    return {
        'user_word_id': uw.id,
        'word_id': w.id,
        'word': w.word,
        'phonetic': w.phonetic or '',
        'meaning': w.meaning,
        'example': w.example or '',
        'example_trans': w.example_trans or '',
        'status': uw.status,
        'is_review': uw.status != 'new',
        'ease_factor': uw.ease_factor,
        'repetitions': uw.repetitions,
        'interval': uw.interval,
        'next_review': uw.next_review.strftime('%Y-%m-%d') if uw.next_review else None
    }

def get_active_vocab_book_ids(user_id):
    uvbs = UserVocabBook.query.filter_by(user_id=user_id, is_active=True).all()
    ids = [uvb.vocab_book_id for uvb in uvbs]
    if not ids:
        default = VocabBook.query.filter_by(is_preset=True).first()
        if default:
            uvb = UserVocabBook(user_id=user_id, vocab_book_id=default.id, is_active=True)
            db.session.add(uvb)
            db.session.commit()
            ids = [default.id]
    return ids

def update_daily_record(user_id, is_new, is_mastered=False):
    today = date.today()
    record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()
    if not record:
        record = DailyRecord(
            user_id=user_id,
            date=today,
            total_count=0,
            new_count=0,
            review_count=0,
            mastered_count=0
        )
        db.session.add(record)
        db.session.flush()
    record.total_count = (record.total_count or 0) + 1
    if is_new:
        record.new_count = (record.new_count or 0) + 1
    else:
        record.review_count = (record.review_count or 0) + 1
    if is_mastered:
        record.mastered_count = (record.mastered_count or 0) + 1
    db.session.commit()

@study_bp.route('/queue', methods=['GET'])
@login_required
def get_queue():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    daily_goal = user.daily_goal if user else 20

    today = date.today()
    today_record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()
    today_new_count = today_record.new_count if today_record else 0
    remaining_new = max(0, daily_goal - today_new_count)

    vocab_ids = get_active_vocab_book_ids(user_id)

    review_uws = UserWord.query.filter(
        UserWord.user_id == user_id,
        UserWord.next_review <= today,
        UserWord.status.in_(['learning', 'mastered', 'new'])
    ).order_by(UserWord.status.asc(), UserWord.next_review.asc()).all()

    new_word_ids_in_user = [uw.word_id for uw in UserWord.query.filter_by(user_id=user_id).all()]
    available_word_ids = [vw.word_id for vw in VocabWord.query.filter(VocabWord.vocab_book_id.in_(vocab_ids)).all()] if vocab_ids else []
    new_word_ids = [wid for wid in available_word_ids if wid not in new_word_ids_in_user]

    new_words_to_add = min(remaining_new, len(new_word_ids))
    new_user_words = []
    for wid in new_word_ids[:new_words_to_add]:
        vbid = None
        for vid in vocab_ids:
            if VocabWord.query.filter_by(vocab_book_id=vid, word_id=wid).first():
                vbid = vid
                break
        uw = UserWord(
            user_id=user_id,
            word_id=wid,
            vocab_book_id=vbid,
            status='new',
            next_review=today
        )
        db.session.add(uw)
        new_user_words.append(uw)

    if new_user_words:
        db.session.commit()

    all_uws = list(review_uws) + new_user_words
    result = [serialize_word_learning(uw) for uw in all_uws]

    return jsonify({
        'code': 200,
        'data': {
            'queue': result,
            'review_count': len(review_uws),
            'new_count': len(new_user_words),
            'total_count': len(result),
            'daily_goal': daily_goal,
            'today_new_done': today_new_count,
            'remaining_new': max(0, remaining_new - len(new_user_words))
        }
    })

@study_bp.route('/review', methods=['POST'])
@login_required
def review_word():
    user_id = get_current_user_id()
    data = request.get_json()
    user_word_id = data.get('user_word_id')
    quality = int(data.get('quality', 0))

    if quality not in [0, 1, 2]:
        return jsonify({'code': 400, 'message': 'quality参数必须是0/1/2'})

    uw = UserWord.query.filter_by(id=user_word_id, user_id=user_id).first()
    if not uw:
        return jsonify({'code': 404, 'message': '记录不存在'})

    is_new = uw.status == 'new'
    old_status = uw.status

    result = SM2Algorithm.calculate(uw, quality)
    uw.repetitions = result['repetitions']
    uw.interval = result['interval']
    uw.ease_factor = result['ease_factor']
    uw.next_review = result['next_review']
    uw.status = result['status']
    uw.last_review = date.today()
    uw.total_reviews += 1
    if quality == 2:
        uw.correct_count += 1

    is_mastered = (old_status != 'mastered' and result['status'] == 'mastered')
    update_daily_record(user_id, is_new, is_mastered)

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': {
            'user_word_id': uw.id,
            'next_review': uw.next_review.strftime('%Y-%m-%d'),
            'status': uw.status,
            'interval': uw.interval,
            'ease_factor': uw.ease_factor,
            'repetitions': uw.repetitions
        }
    })

@study_bp.route('/today-summary', methods=['GET'])
@login_required
def today_summary():
    user_id = get_current_user_id()
    user = User.query.get(user_id)
    daily_goal = user.daily_goal if user else 20

    today = date.today()
    record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()

    review_due = UserWord.query.filter(
        UserWord.user_id == user_id,
        UserWord.next_review <= today,
        UserWord.status.in_(['learning', 'mastered'])
    ).count()

    return jsonify({
        'code': 200,
        'data': {
            'daily_goal': daily_goal,
            'today_new': record.new_count if record else 0,
            'today_review': record.review_count if record else 0,
            'today_total': record.total_count if record else 0,
            'today_mastered': record.mastered_count if record else 0,
            'review_due': review_due,
            'goal_progress': min(100, int(((record.new_count if record else 0) / daily_goal) * 100)) if daily_goal > 0 else 0
        }
    })

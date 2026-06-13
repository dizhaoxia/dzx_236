from flask import Blueprint, request, jsonify
from models import db, User, UserWord, DailyRecord
from utils.auth import login_required, get_current_user_id
from datetime import datetime, timedelta, date
from sqlalchemy import func

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/summary', methods=['GET'])
@login_required
def summary():
    user_id = get_current_user_id()

    total_words = UserWord.query.filter_by(user_id=user_id).count()
    mastered = UserWord.query.filter_by(user_id=user_id, status='mastered').count()
    learning = UserWord.query.filter_by(user_id=user_id, status='learning').count()
    new_count = UserWord.query.filter_by(user_id=user_id, status='new').count()

    study_days = DailyRecord.query.filter(DailyRecord.user_id == user_id, DailyRecord.total_count > 0).count()

    today = date.today()
    streak = 0
    d = today
    while True:
        r = DailyRecord.query.filter_by(user_id=user_id, date=d).first()
        if r and r.total_count > 0:
            streak += 1
            d = d - timedelta(days=1)
        else:
            break

    total_new = db.session.query(func.coalesce(func.sum(DailyRecord.new_count), 0)).filter_by(user_id=user_id).scalar()
    total_review = db.session.query(func.coalesce(func.sum(DailyRecord.review_count), 0)).filter_by(user_id=user_id).scalar()
    total_mastered_all = db.session.query(func.coalesce(func.sum(DailyRecord.mastered_count), 0)).filter_by(user_id=user_id).scalar()

    today_record = DailyRecord.query.filter_by(user_id=user_id, date=today).first()

    return jsonify({
        'code': 200,
        'data': {
            'total_words': total_words,
            'mastered': mastered,
            'learning': learning,
            'new': new_count,
            'study_days': study_days,
            'streak': streak,
            'total_new': total_new,
            'total_review': total_review,
            'total_mastered': total_mastered_all,
            'today': {
                'new': today_record.new_count if today_record else 0,
                'review': today_record.review_count if today_record else 0,
                'total': today_record.total_count if today_record else 0,
                'mastered': today_record.mastered_count if today_record else 0
            }
        }
    })

@stats_bp.route('/calendar', methods=['GET'])
@login_required
def calendar():
    user_id = get_current_user_id()
    end_date = date.today()
    start_date = end_date - timedelta(days=365)

    records = DailyRecord.query.filter(
        DailyRecord.user_id == user_id,
        DailyRecord.date >= start_date,
        DailyRecord.date <= end_date
    ).all()

    data = {}
    for r in records:
        if r.total_count > 0:
            data[r.date.strftime('%Y-%m-%d')] = {
                'total': r.total_count,
                'new': r.new_count,
                'review': r.review_count,
                'mastered': r.mastered_count
            }

    return jsonify({
        'code': 200,
        'data': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d'),
            'records': data
        }
    })

@stats_bp.route('/trend', methods=['GET'])
@login_required
def trend():
    user_id = get_current_user_id()
    days = int(request.args.get('days', 30))
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    records = DailyRecord.query.filter(
        DailyRecord.user_id == user_id,
        DailyRecord.date >= start_date,
        DailyRecord.date <= end_date
    ).all()

    record_map = {r.date: r for r in records}

    dates = []
    new_data = []
    review_data = []
    total_data = []
    mastered_data = []

    for i in range(days):
        d = start_date + timedelta(days=i)
        dates.append(d.strftime('%Y-%m-%d'))
        r = record_map.get(d)
        new_data.append(r.new_count if r else 0)
        review_data.append(r.review_count if r else 0)
        total_data.append(r.total_count if r else 0)
        mastered_data.append(r.mastered_count if r else 0)

    return jsonify({
        'code': 200,
        'data': {
            'dates': dates,
            'new': new_data,
            'review': review_data,
            'total': total_data,
            'mastered': mastered_data
        }
    })

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.word import word_bp
from routes.study import study_bp
from routes.stats import stats_bp
from routes.vocab import vocab_bp
import os
import pymysql

def create_database():
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database {Config.MYSQL_DB} ready")
    except Exception as e:
        print(f"Database init warning: {e}")

def create_app():
    create_database()
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    with app.app_context():
        from models import User, Word, UserWord, VocabBook, UserVocabBook, DailyRecord, VocabWord
        db.create_all()
        from init_data import init_vocab_books
        init_vocab_books()

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(word_bp, url_prefix='/api/word')
    app.register_blueprint(study_bp, url_prefix='/api/study')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(vocab_bp, url_prefix='/api/vocab')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Vocab Master API running'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=3232, debug=True)

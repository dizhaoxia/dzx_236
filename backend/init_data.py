import os
import json
from models import db, Word, VocabBook, VocabWord

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def init_vocab_books():
    if VocabBook.query.count() > 0:
        return

    preset_books = [
        {'name': '英语四级核心词汇', 'description': '大学英语四级考试核心高频词汇，约4000词', 'file': 'cet4.json'},
        {'name': '英语六级核心词汇', 'description': '大学英语六级考试核心高频词汇，约4000词', 'file': 'cet6.json'},
        {'name': '考研英语词汇', 'description': '研究生入学考试英语核心词汇，约5500词', 'file': 'kaoyan.json'},
    ]

    for book_info in preset_books:
        book = VocabBook(name=book_info['name'], description=book_info['description'], is_preset=True)
        db.session.add(book)
        db.session.flush()

        words_data = load_json(book_info['file'])
        for w in words_data:
            existing = Word.query.filter_by(word=w['word']).first()
            if not existing:
                word = Word(
                    word=w['word'],
                    phonetic=w.get('phonetic', ''),
                    meaning=w.get('meaning', ''),
                    example=w.get('example', ''),
                    example_trans=w.get('example_trans', '')
                )
                db.session.add(word)
                db.session.flush()
                word_id = word.id
            else:
                word_id = existing.id

            vw = VocabWord(vocab_book_id=book.id, word_id=word_id)
            db.session.add(vw)

    db.session.commit()
    print('Preset vocab books initialized')

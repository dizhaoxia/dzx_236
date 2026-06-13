from datetime import datetime, timedelta

class SM2Algorithm:
    MIN_EASE_FACTOR = 1.3

    @staticmethod
    def calculate(user_word, quality):
        repetitions = user_word.repetitions or 0
        interval = user_word.interval or 0
        ease_factor = user_word.ease_factor or 2.5

        if quality == 0:
            repetitions = 0
            interval = 0
        elif quality == 1:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 3
            else:
                interval = round(interval * ease_factor * 0.6)
            ease_factor = max(SM2Algorithm.MIN_EASE_FACTOR, ease_factor - 0.15)
        elif quality == 2:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 6
            else:
                interval = round(interval * ease_factor)
            ease_factor = ease_factor + 0.1

        if quality > 0:
            repetitions += 1

        if repetitions >= 3 and quality == 2:
            status = 'mastered'
        elif repetitions >= 1:
            status = 'learning'
        else:
            status = 'new'

        new_next_review = datetime.now().date() + timedelta(days=interval)

        return {
            'repetitions': repetitions,
            'interval': interval,
            'ease_factor': round(ease_factor, 2),
            'next_review': new_next_review,
            'status': status
        }

    @staticmethod
    def is_due_today(user_word):
        if not user_word.next_review:
            return True
        return user_word.next_review <= datetime.now().date()

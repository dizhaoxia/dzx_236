import requests

BASE = 'http://127.0.0.1:3232/api'

r = requests.post(f'{BASE}/auth/login', json={'email': 'test@example.com', 'password': 'test123456'})
print('Login:', r.status_code)
data = r.json()
print('Login msg:', data.get('message'))
token = data['data']['token']
headers = {'Authorization': f'Bearer {token}'}

r = requests.get(f'{BASE}/study/queue', headers=headers)
data = r.json()
print('Queue count:', len(data['data']['queue']))
q = data['data']['queue']
if q:
    uw = q[0]
    print('First word:', uw['user_word_id'], uw['word'])
    r2 = requests.post(f'{BASE}/study/review', headers=headers, json={
        'user_word_id': uw['user_word_id'],
        'quality': 2
    })
    print('Review status:', r2.status_code)
    print('Review result:', r2.json())
else:
    print('No queue items - need more words')

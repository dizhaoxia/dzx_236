import hashlib
import secrets
import pymysql

password = 'test123456'
salt = secrets.token_hex(16)
hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
hashed = f"{salt}${hash_obj.hex()}"
print('New hash:', hashed)

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='vocab_master')
cur = conn.cursor()
cur.execute("UPDATE users SET password = %s WHERE email = 'test@example.com'", (hashed,))
conn.commit()
print('Password updated')
cur.close()
conn.close()

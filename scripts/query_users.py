import pymysql

conn = pymysql.connect(host='127.0.0.1', user='chauhan', password='saurav', db='registration_db', port=3306)
cur = conn.cursor()

cur.execute("DESCRIBE users;")
cols = cur.fetchall()
print('COLUMNS:')
for r in cols:
    print(r)

cur.execute('SELECT id, name, email, is_active, is_staff, created_at FROM users ORDER BY id DESC LIMIT 5;')
rows = cur.fetchall()
print('\nLAST ROWS:')
for r in rows:
    print(r)

cur.close()
conn.close()

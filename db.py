import sqlite3
from openai import OpenAI
from cfg import api_key
conn = sqlite3.connect('ids.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS ids (id TEXT PRIMARY KEY)''')
c.execute('''
    CREATE TABLE IF NOT EXISTS binhluan (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        articleId TEXT UNIQUE,
        articleLink TEXT UNIQUE,
        text TEXT
    )
''')


def getbinhluan(text):
    client = OpenAI(
        api_key=api_key,
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Hãy cho một đoạn bình luận hoặc nhận xét ngắn gọn, xúc tích về vụ việc trên căn cứ trên một số luật lệ hoặc quy định hiện hành ( thêm hightling chỗ quan trọng)",
            },
            {
                'role': 'user',
                'content': text
            }
        ],
        temperature=0.2,
        max_tokens=2056,

        # request_timeout=config.REQUEST_TIMEOUT,
        model='gpt-4o-mini',
    )
    response = chat_completion.choices[0].message.content
    return response

def add_comment_if_not_exists(articleId, articleLink, text):
    # Kiểm tra xem articleId hoặc articleLink đã tồn tại chưa
    c.execute('''
            SELECT text FROM binhluan
            WHERE articleId = ? OR articleLink = ?
        ''', (articleId, articleLink))

    result = c.fetchone()

    if result is None:
        text = getbinhluan(text)
        # Nếu chưa tồn tại, thêm mới
        c.execute('''
                INSERT INTO binhluan (articleId, articleLink, text)
                VALUES (?, ?, ?)
            ''', (articleId, articleLink, text))
        conn.commit()
        return text
    else:
        # Nếu đã tồn tại, trả về text hiện có
        existing_text = result[0]
        return existing_text

def id_exists(id):
    c.execute('SELECT 1 FROM ids WHERE id=?', (id,))
    return c.fetchone() is not None

def add_id(id):
    c.execute('INSERT OR IGNORE INTO ids (id) VALUES (?)', (id,))
    conn.commit()

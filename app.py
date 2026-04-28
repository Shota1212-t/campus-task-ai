from flask import Flask, request, redirect
import sqlite3
import os
from dotenv import load_dotenv
from google import genai
from datetime import date, datetime

app = Flask(__name__)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            deadline TEXT
        )
    """)

    conn.commit()
    conn.close()

def days_until(deadline_str):
    today = date.today()
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
    return (deadline - today).days

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        task = request.form["task"].strip()
        deadline = request.form["deadline"].strip()
        today = str(date.today())

        if deadline < today:
            return """
            <script>
                alert('締切日は今日以降を入力してください');
                window.location.href = '/';
            </script>
            """

        if task == "" or deadline == "":
            return """
            <script>
                alert('課題名と締切日を入力してください');
                window.location.href = '/';
            </script>
            """

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO tasks (task, deadline) VALUES (?, ?)",
            (task, deadline)
        )

        conn.commit()
        conn.close()

        return """
        <script>
        window.location.href='/';
        </script>
        """

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, task, deadline
        FROM tasks
        ORDER BY deadline ASC
    """)

    tasks = cur.fetchall()
    conn.close()

    today = str(date.today())

    # 課題リストのHTML生成
    if len(tasks) == 0:
        tasks_html = '<p style="text-align:center;padding:2rem;color:var(--color-text-secondary);font-size:14px;">課題はまだありません 🎉</p>'
    else:
        tasks_html = ""
        for t in tasks:
            d = days_until(t[2])
            if d <= 1:
                dot_class = "dot-urgent"
                badge_class = "badge-urgent"
                badge_text = "明日" if d == 1 else "今日"
            elif d <= 5:
                dot_class = "dot-soon"
                badge_class = "badge-soon"
                badge_text = f"{d}日後"
            else:
                dot_class = "dot-ok"
                badge_class = "badge-ok"
                badge_text = "余裕あり"

            deadline_display = t[2][5:]  # MM-DD だけ表示

            tasks_html += f"""
            <div class="task-item">
                <div class="task-dot {dot_class}"></div>
                <span class="task-name">{t[1]}</span>
                <span class="task-deadline">{deadline_display}</span>
                <span class="task-badge {badge_class}">{badge_text}</span>
                <a href="/delete/{t[0]}" class="del-btn" onclick="return confirm('この課題を削除しますか？')" title="削除">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="#E24B4A" stroke-width="2" stroke-linecap="round">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </a>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campus Task AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=DM+Mono&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Noto Sans JP', sans-serif;
            background: #f5f4f0;
            min-height: 100vh;
            padding: 0 0 4rem;
            color: #1a1a1a;
        }}

        .wrap {{
            max-width: 640px;
            margin: 0 auto;
            padding: 2rem 1.25rem;
        }}

        /* ヘッダー */
        .header {{
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #e2e0d8;
        }}

        .header-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            background: #1D9E75;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }}

        .header h1 {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: #111;
        }}

        .header p {{
            font-size: 12px;
            color: #888;
            margin-top: 2px;
        }}

        /* セクション */
        .section {{ margin-bottom: 1.75rem; }}

        .section-label {{
            font-size: 11px;
            font-weight: 500;
            color: #888;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        /* カード */
        .card {{
            background: #fff;
            border: 1px solid #e2e0d8;
            border-radius: 14px;
            padding: 1.25rem;
        }}

        /* フォーム */
        .form-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 12px;
        }}

        .form-group {{ display: flex; flex-direction: column; gap: 6px; }}

        .form-group label {{
            font-size: 12px;
            color: #666;
            font-weight: 500;
        }}

        .form-group input {{
            padding: 9px 12px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: 'Noto Sans JP', sans-serif;
            color: #111;
            background: #fafaf8;
            outline: none;
            transition: border-color 0.15s, box-shadow 0.15s;
        }}

        .form-group input:focus {{
            border-color: #1D9E75;
            box-shadow: 0 0 0 3px rgba(29,158,117,0.12);
            background: #fff;
        }}

        .btn-add {{
            width: 100%;
            padding: 10px;
            background: #1D9E75;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            font-family: 'Noto Sans JP', sans-serif;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: background 0.15s;
        }}

        .btn-add:hover {{ background: #0F6E56; }}
        .btn-add:active {{ transform: scale(0.98); }}

        /* 課題一覧ヘッダー */
        .tasks-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }}

        .ai-btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            padding: 5px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            color: #555;
            background: #fff;
            cursor: pointer;
            font-family: 'Noto Sans JP', sans-serif;
            text-decoration: none;
            transition: background 0.15s;
        }}

        .ai-btn:hover {{ background: #f5f4f0; }}

        /* タスクアイテム */
        .tasks-card {{
            background: #fff;
            border: 1px solid #e2e0d8;
            border-radius: 14px;
            overflow: hidden;
        }}

        .task-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 11px 14px;
            transition: background 0.12s;
        }}

        .task-item:hover {{ background: #fafaf8; }}
        .task-item + .task-item {{ border-top: 1px solid #f0ede8; }}

        .task-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .dot-urgent {{ background: #E24B4A; }}
        .dot-soon   {{ background: #EF9F27; }}
        .dot-ok     {{ background: #1D9E75; }}

        .task-name {{
            flex: 1;
            font-size: 14px;
            color: #111;
        }}

        .task-deadline {{
            font-size: 12px;
            color: #999;
            font-family: 'DM Mono', monospace;
        }}

        .task-badge {{
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 20px;
            font-weight: 500;
            flex-shrink: 0;
        }}

        .badge-urgent {{ background: #FCEBEB; color: #A32D2D; }}
        .badge-soon   {{ background: #FAEEDA; color: #854F0B; }}
        .badge-ok     {{ background: #EAF3DE; color: #3B6D11; }}

        .del-btn {{
            width: 26px;
            height: 26px;
            border-radius: 6px;
            background: transparent;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            opacity: 0;
            transition: opacity 0.15s, background 0.15s;
            text-decoration: none;
            flex-shrink: 0;
        }}

        .task-item:hover .del-btn {{ opacity: 1; }}
        .del-btn:hover {{ background: #FCEBEB; }}
    </style>
</head>
<body>
    <div class="wrap">

        <!-- ヘッダー -->
        <div class="header">
            <div class="header-icon">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/>
                    <rect x="9" y="3" width="6" height="4" rx="1"/>
                    <path d="M9 12h6M9 16h4"/>
                </svg>
            </div>
            <div>
                <h1>Campus Task AI</h1>
                <p>課題を管理して、AIにアドバイスをもらおう</p>
            </div>
        </div>

        <!-- 課題追加フォーム -->
        <div class="section">
            <div class="section-label">課題を追加</div>
            <div class="card">
                <form method="post">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="task">課題名</label>
                            <input type="text" id="task" name="task" placeholder="例：レポート提出" required>
                        </div>
                        <div class="form-group">
                            <label for="deadline">締切日</label>
                            <input type="date" id="deadline" name="deadline" min="{today}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn-add">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                        </svg>
                        追加する
                    </button>
                </form>
            </div>
        </div>

        <!-- 課題一覧 -->
        <div class="section">
            <div class="tasks-header">
                <div class="section-label" style="margin-bottom:0">課題一覧</div>
                <a href="/ai" class="ai-btn">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                    </svg>
                    AIに相談する
                </a>
            </div>
            <div class="tasks-card">
                {tasks_html}
            </div>
        </div>

    </div>
</body>
</html>"""

    return html

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM tasks WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/ai")
def ai():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT task, deadline FROM tasks ORDER BY deadline ASC")
    tasks = cur.fetchall()

    conn.close()

    if len(tasks) == 0:
        return """<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8"><title>AIアドバイス</title></head>
<body style="font-family:sans-serif;padding:2rem">
<h1>AIアドバイス</h1>
<p>課題がまだありません。</p>
<a href="/">戻る</a>
</body></html>"""

    task_text = ""
    for t in tasks:
        task_text += f"- {t[0]}（締切: {t[1]}）\n"

    prompt = f"""
あなたは大学生向けの学習アシスタントです。

以下の課題一覧をもとに、
1. 優先順位
2. 今週やるべきこと
3. 具体的な行動計画

をわかりやすく日本語で提案してください。

課題一覧：
{task_text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        ai_text = response.text
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            ai_text = "⚠️ APIのリクエスト上限に達しました。しばらく待ってから再試行してください。"
        else:
            ai_text = f"⚠️ エラーが発生しました: {e}"

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIアドバイス - Campus Task AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans JP', sans-serif; background: #f5f4f0; min-height: 100vh; padding: 0 0 4rem; color: #1a1a1a; }}
        .wrap {{ max-width: 640px; margin: 0 auto; padding: 2rem 1.25rem; }}
        .back-btn {{ display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #666; text-decoration: none; margin-bottom: 1.5rem; }}
        .back-btn:hover {{ color: #111; }}
        h1 {{ font-size: 20px; font-weight: 700; margin-bottom: 1.25rem; }}
        .card {{ background: #fff; border: 1px solid #e2e0d8; border-radius: 14px; padding: 1.5rem; white-space: pre-wrap; font-size: 14px; line-height: 1.8; }}
    </style>
</head>
<body>
    <div class="wrap">
        <a href="/" class="back-btn">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
            </svg>
            戻る
        </a>
        <h1>AIアドバイス</h1>
        <div class="card">{ai_text}</div>
    </div>
</body>
</html>"""

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
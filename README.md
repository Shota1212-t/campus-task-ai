# Campus Task AI
大学生向けの課題管理アプリです。  
Flask + SQLite + Gemini API を使って、課題管理とAIによる学習アドバイスを提供します。

---

## 機能

- 課題の追加・削除
- 締切日の管理
- 締切の近い課題の優先表示
- AIによる学習アドバイス（Gemini API）
- 「今日やるべきこと」の自動提案

---

## AI機能について

Google Gemini API を利用し、登録された課題データをもとに以下を生成します：

- 課題の優先順位
- 今週やるべきこと
- 具体的な学習計画

---

## 使用技術

- Python 3
- Flask
- SQLite
- Google Gemini API
- HTML / CSS（自作UI）

---

## セットアップ方法

### 1. リポジトリをクローン

```bash
git clone https://github.com/ユーザー名/campus-task-ai.git
cd campus-task-ai
```

### 2. 仮想環境

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. 必要ライブラリ

```bash
pip install flask python-dotenv google-genai
```

### 4. APIキー設定

.env ファイルを作成：

```bash
GEMINI_API_KEY=あなたのAPIキー
```

### 5. 実行

```bash
python app.py
```

### 工夫した点

締切日までの日数で色分け表示
UIをシンプルで見やすく設計
AIに課題データを渡して学習支援を自動化
削除確認・バリデーションを実装

### 今後の改善予定

ログイン機能
完了チェック機能
スマホ対応強化
AIによる1日の学習スケジュール生成

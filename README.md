# Django Team Workflow

SOF203 exercise 13 用の Django ToDo アプリです。Django のチーム開発を、Issue、feature branch、Pull Request、CI の流れで練習するために使用します。

## 主な機能

- タスクの作成と一覧表示
- 投稿日時順、期限順での並び替え
- タスク詳細の表示
- タスクの編集、完了、削除
- Django CI による lint とテスト
- Render Blueprint を使ったデプロイ

## ローカルセットアップ

Python 3.10 での実行を想定しています。

```sh
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

起動後、`http://127.0.0.1:8000/` をブラウザで開いて確認します。

## テスト

```sh
python manage.py test
```

Pull Request では GitHub Actions でも同じテストが実行されます。

## 開発フロー

1. 対応する Issue を作成または選択する
2. `main` から作業用ブランチを作成する
3. 変更とテストをコミットして push する
4. `main` 向けの Pull Request を作成する
5. CI とレビューを確認してからマージする

`main` は保護されているため、変更は Pull Request 経由で取り込みます。

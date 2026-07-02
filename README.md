# Django Team Workflow

SOF203 exercise 13 用の Django ToDo アプリです。

## PM が用意したもの

- Django ToDo アプリの土台
- タスク一覧、詳細ページ
- Django CI
- `main` ブランチを保護して、変更は Pull Request 経由にする運用

## メンバーが Pull Request で行うこと

授業スライドの内容に沿って、feature branch を作成してから Pull Request を出してください。

- タスク編集ページを追加する
- 編集内容を保存する view と URL を追加する
- 必要なテストを追加する
- Render デプロイ用の設定を追加する

## 確認コマンド

```sh
python manage.py test
```

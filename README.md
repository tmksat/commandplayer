# commandplayer

commandplayerは、カスタマイズ可能なGUIベースのコマンド実行ツールです。
Pythonで開発されており、Tkinterを使用してユーザーフレンドリーなインターフェースを提供します。
このツールは、頻繁に使用するコマンドやスクリプトを効率的に管理し、実行するのに役立ちます。



## 主な機能

- カスタマイズ可能なコマンドボタン
- 動的なボタンの追加・削除
- コマンド実行結果の表示
- コマンドの編集機能
- 設定のJSON形式での保存と読み込み
- 出力のクリア機能



## 必要条件

- Python 3.6以上
- Tkinter（通常はPythonに標準で含まれています）



## インストール

```shell
$ cd commandplayer
$ python3 -m venv .
$ source ./bin/activate
$ pip3 install -r requrements.txt
$ python3 -m commandplayer
```



## 使用方法

1. スクリプトを実行します：

```shell
$ python3 -m commandplayer
```

2. GUIウィンドウが開きます。デフォルトで5つのコマンドボタンが表示されます。

3. 各ボタンの隣にある「Edit」ボタンをクリックして、ボタン名とコマンドを編集できます。

4. 「Add Button」をクリックして新しいコマンドボタンを追加できます。

5. 「Remove Button」をクリックして最後のコマンドボタンを削除できます。

6. コマンドボタンをクリックすると、対応するコマンドが実行され、結果が右側のテキストエリアに表示されます。

7. 「Clear Output」ボタンをクリックして、出力テキストエリアをクリアできます。

8. 「Exit」ボタンをクリックしてアプリケーションを終了します。




## カスタマイズ

コマンドの設定は`commands.json`ファイルに保存されます。このファイルを直接編集することで、アプリケーション外からもコマンドを管理できます。




## ライセンス

このプロジェクトは[MITライセンス](https://choosealicense.com/licenses/mit/)の下で公開されています。



## 連絡先

Tomoki Sato - [@tmksat](https://twitter.com/tmksat)

プロジェクトリンク: [https://github.com/tmksat/commandplayer](https://github.com/tmksat/commandplayer)

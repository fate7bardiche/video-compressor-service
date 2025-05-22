# 作業段階をブランチで分けています、今回stage2
開発段階に応じて、ブランチが分かれています。

- stage1: ファイルをアップロードできる機能まで実装
- stage2: 動画処理の内容を選択しファイルをアップロード。その後動画処理が行われ、処理後のファイルをダウンロードできる機能まで実装

**stage2** ブランチが完成版です。

詳細や使用方法は各ブランチのREADMEに記載しています。

# video-compressor-service
ソケットを通じて動画ファイルをアップロードし、様々な動画処理を行えるCLIアプリケーション

## 目次
- [使用技術](#使用技術)
- [環境構築](#環境構築)
  - [clone](#clone)
  - [実行](#実行)
    - [server側](#server側)
    - [client側](#client側)
- [使い方](#使い方)
  - [サーバーに接続](#サーバーに接続)
  - [ファイルの選択](#ファイルの選択)
  - [実行したい動画処理を選択](#実行したい動画処理を選択)
  - [動画処理に必要なパラメータを入力する](#動画処理に必要なパラメータを入力する)
  - [アップロード](#アップロード)
  - [動画処理の実施 & 進捗確認](#動画処理の実施--進捗確認)
  - [作成されたファイルのダウンロード](#作成されたファイルのダウンロード)
- [実行中のビデオキャプチャ](#実行中のビデオキャプチャ)

## 使用技術

![Python](https://img.shields.io/badge/-Python-F9DC3E.svg?style=flat&logo=python)： 3.10.12  
![Linux](https://img.shields.io/badge/-Linux-FCC624?style=flat&logo=linux&logoColor=black)：Ubuntu 22.04  
![FFmpeg Badge](https://img.shields.io/badge/-FFmpeg-007808?style=flat&logo=ffmpeg)： 4.4.2  
![ffmpeg-python Badge](https://img.shields.io/badge/-ffmpeg--python-3775A9?style=flat&logo=ffmpeg&logoColor=F9DC3E)： 0.2.0


## 環境構築
### clone
```
$ git clone git@github.com:fate7bardiche/video-compressor-service.git
$ cd video-compressor-service
```

### 実行
server側とclient側は、別のタブで実行してください。
先にサーバー側から実行します。


#### server側
```
$ pwd
> ~/video-compressor-service/server
$ python3 server.py 
```

#### client側
```
$ pwd
> ~/video-compressor-service/client
$ python3 client.py 
```

## 使い方
server側のタブ内を操作することはありません。  
クライアント側のタブから、指示に従って入力します。

### サーバーに接続
client側を実行すると、自動的にserverに接続します。  
同一のIPアドレスがすでに接続は、接続できません。

<img width="1210" alt="スクリーンショット 2025-05-23 2 10 13" src="https://github.com/user-attachments/assets/37a61a03-adca-4d24-98a8-ddb52b97af34" />

### ファイルの選択
`client/video`ディレクトリに置いてある動画が選択肢に表示されるので、選択してください。

<img width="1428" alt="スクリーンショット 2025-05-23 2 17 46" src="https://github.com/user-attachments/assets/de166c90-b983-453e-ab33-db490d4a910d" />

### 実行したい動画処理を選択
選択した動画に対して、実行したい動画処理を選択します。

<img width="373" alt="スクリーンショット 2025-05-23 2 18 35" src="https://github.com/user-attachments/assets/15654496-f40e-4d3c-91fc-8d1f9d5b38aa" />

### 動画処理に必要なパラメータを入力する
選択した動画処理に応じて、必要なパラメータを入力します。  
各処理ごとに、必要なパラメータは異なるので案内に従って入力します。

<img width="376" alt="スクリーンショット 2025-05-23 2 18 44" src="https://github.com/user-attachments/assets/d426939f-fdee-4e25-b0f5-f65d66f86da7" />

### アップロード
最後のパラメータが入力しEnterを押下すると、動画ファイルがserver側にアップロードされます。  
client側には、現在何バイト送信したのか分かるように進捗が表示されます。

<img width="755" alt="スクリーンショット 2025-05-23 2 19 13" src="https://github.com/user-attachments/assets/d7b5e6c1-936d-4343-a097-7ce9736cdeca" />

### 動画処理の実施 & 進捗確認
動画が正しくアップロードされると、server側で動画処理が実施されます。  
処理状況は60経過するごとにclientに送信されます。

<img width="975" alt="スクリーンショット 2025-05-23 2 20 22" src="https://github.com/user-attachments/assets/ce2a021f-9b63-4f19-a965-15f9c298a012" />

### 作成されたファイルのダウンロード
動画処理が正しく完了すると、作成されたファイルのダウンロードが開始します。  
ダウンロードされたファイルは、`client/edited_video`ディレクトリに保存されます。

<img width="976" alt="スクリーンショット 2025-05-23 2 22 18" src="https://github.com/user-attachments/assets/98754693-9115-4f63-9a60-789bc584b731" />

## 実行中のビデオキャプチャ
基本的な操作は、以下のキャプチャを参考にしてください。

https://github.com/user-attachments/assets/9f956190-b68f-45cf-bc1e-d98e677f3fa9

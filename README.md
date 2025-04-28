# 作業段階をブランチで分けています、今回stage1
開発段階に応じて、ブランチが分かれています。

- stage1: ファイルをアップロードできる機能まで実装
- stage2: ファイルをアップロードした後に動画処理が行われ、処理後のファイルをダウンロードできる機能まで実装

**stage2** ブランチが完成版です。

詳細や使用方法は各ブランチのREADMEに記載しています。

# video-compressor-service
ソケットを通じて動画ファイルをアップロードし、様々な動画処理を行えるCLIアプリケーション

## 使用技術
![Static Badge](https://img.shields.io/badge/-Python-F9DC3E.svg?style=flat&logo=python)： 3.10.12  
![Static Badge](https://img.shields.io/badge/-Linux-FCC624?style=flat&logo=linux&logoColor=black)：Ubuntu 22.04  

## 環境構築
### clone
```
$ git clone git@github.com:fate7bardiche/video-compressor-service.git
$ cd video-compressor-service
```

## 使い方
serverとclientでタブを分けて起動します。

### server側
```
$ pwd
> ~/video-compressor-service/server
$ python3 server.py 
```
### client側
stage1では、ファイルの選択機能はありません。  
client側を実行すると、`/video-compressor-service/client/video/example.mp4`が動的に選択され、ファイルがserver側にアップロードされます。
```
$ pwd
> ~/video-compressor-service/client
$ python3 client.py 
```
アップロード後のファイルは`/video-compressor-service/server/video/` ディレクトリに格納されます。

## 実行中のキャプチャ
https://github.com/user-attachments/assets/6fa0b498-6d26-4421-9f1e-11d3ee376b88
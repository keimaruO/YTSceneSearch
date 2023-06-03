# YTSceneSearch

YTSceneSearchは、思い出せそうで思い出せないシーンを自分が覚えてる単語を複数入力すれば該当シーンがでてくる確率がぐーんと上がる字幕検索アプリ

検索結果には時間指定付きのURLが含まれていて、該当シーンをワンクリックでブラウザで開けます。わ～便利～w

YouTubeの自動生成字幕を利用してシーン検索を行います。



# 使用例

どの配信どのシーンで言ってたか探すのに使えます。

切り抜き動画の概要欄に元動画が記載されてない場合に使えます。(昔は元動画貼るガイドラインがまだなかったので)


# モデル配布

自分がホロライブの字幕検索のためだけに作ってたので今はホロ専用です。

2017/09/07～2023/04/18までの全員分の字幕あります。
https://huggingface.co/datasets/keimaru/JP_Holo_Subtitles/tree/main

(更新 23/06/04) チャットバージョンも作りました。
https://huggingface.co/keimaru/JP_Holo_chat/tree/main

# 使い方

# 下記の方法でファイルをダウンロードします。
![image](https://github.com/keimaruO/YTSceneSearch/assets/91080250/2ce79d79-ff49-47db-8622-da319e101f32)
![image](https://github.com/keimaruO/YTSceneSearch/assets/91080250/73d49cad-3281-43cc-9312-d349cb82503d)



# 次にダウンロードしたexeを開いて、[Browse]を押してファイルを選択してください。


# 検索欄の使い方を説明します。
1にはっきり、絶対に言っていたと確信できる単語をいれる
2が多分言ってたであろう単語をいれる
3にも多分言ってたであろう単語をいれる(3にも単語をいれると1,2,3の単語全てを含む検索になる)


`|`記号使ってOR検索に対応してます

![image](https://github.com/keimaruO/YTSceneSearch/assets/91080250/0114a771-c52f-4ec1-9aba-dd2fcdc0eb31)


Now Loading...の表示が消えれば検索終了

Ctrlキーを押しながらURLをクリックするとウィンドウが維持されたままブラウザで開けます。


# 検索のコツ

YouTubeの自動生成字幕を使用しているので、AIが聞き取れる可能性が高く、記憶を辿って実際に話していた確率の高い単語を入力して、字幕の変換エラーも考慮して類似した単語を入れる

例: うんち|ウンチ|運痴|音痴

`|`のOR検索を使ってよりヒットするようにする。

一文字でも検索できます。

例　❌「昨日の」
　　❌「昨日」
　　⭕「昨」

ですが一文字で検索すると「昨夜」「昨晩」「昨今」などもヒットして処理時間増加したり、検索結果が膨大になったりします、工夫して使ってください。

1に入れた単語が基盤となって検索するので一番重要です。


# アルゴリズム

簡単に説明するとまず

検索欄1に入力されたキーワード(主要なキーワード)が含まれる行を探す。
↓
これが見つかると、その行を中心以前50行(これを「検索範囲」)を設定
↓
この「検索範囲」内で、検索欄2と検索欄3に入力された追加のキーワードが存在する行を探す。


もっと大昔に作ったのをとりまそっこうgithubに公開しただけなので、コードやらアルゴリズムやら機能も薄いですが、今後より精度が上がる方法を思いついたり皆さんから教えてもらえたら実装します。

.srt形式の字幕ファイルを特殊な形式に改造して使用してます。なんで通常のsrtでは利用できませんがその変換プログラムは後日配布予定

なんかあれば気軽に連絡どうぞ～

マシュマロ https://marshmallow-qa.com/keimaru114514
Discord keimaru#7680
Twitter @keimaru114514


> YTSceneSearchは、 Apache 2.0ライセンスで配布されているライブラリが含まれています。

# デスクトップアプリ作成課題
検索課題で作った検索ツールをデスクトップアプリとして
操作性を高め、より価値の高いものにするための課題です。
これを習得すると＋月２万円ほどの収入増加が見込めます。

view.pyがメインの実行ファイルです。これを実行するとデスクトップアプリが
表示されます。

説明：https://youtu.be/UsgiZGYkZrY<br>
参考サイト：https://qiita.com/inoory/items/f431c581332c8d500a3b<br>
完成形：https://youtu.be/wBi6_DcfRGQ<br>

# 1
HTML使い検索ワード入力と検索ボタンを作ってください
htmlフォルダ内のindex.htmlに対してHTMLタグを用いて追加してください

# 2
検索ワード入力が空だったらアラートを表示させ、検索はしないようにしてください

# 3
検索結果をデスクトップアプリの画面に表示できるようにtextareaタグを使って
ログ表示領域を作成してください。

# 4
作成したログ表示領域にkimetsu_searchの結果を表示できるようにしてください

# 5
ログ表示領域が小さいので大きく表示できるようにclassを定義して、style.cssに処理を記述してください

# 6
CSVファイルの保存先をHTML画面から指定できるようにしてください

# 7
Pyinstallerを使って、１つの実行可能ファイルにパッケージ化してみよう。  <br>
pipでpyinstallerインストール後に以下コマンドを実行してみよう。<br>
`python -m eel <はじめに起動するpyファイル> <htmlのフォルダ名> --onefile`

python以外のファイルを追加したい場合は以下
```
python -m eel <はじめに起動するpyファイル> <htmlのフォルダ名> --onefile --add-data '追加したいファイル名;パッケージファイルの追加先'
```

例:.envファイルを追加
```
python -m eel <はじめに起動するpyファイル> <htmlのフォルダ名> --onefile --add-data '.env;.'
```
pyinstaller実行後、distフォルダに実行可能フィイル(exe等)が格納されます。<br>
顧客提供時は、このファイルを提供することでpythonのインストールは不要になります。<br>
ただし、exeに含まれるのはpyファイルのみです。そのためcsv等の外部ファイルは<br>
別途提供する必要があります。


# おまけ
bootstrapを適用して、キレイな画面を作成してみてください。  
以下のサイトのスターターテンプレートを適用し、レイアウトを調整してみてください。  
https://getbootstrap.jp/docs/4.3/getting-started/introduction/


import dash_html_components as html 
import dash_core_components as dcc 

memo_style = {"fontFamily": "Arial"}

layout = html.Div([
    

    html.H1("Covid-19の感染データメモ", style={"textAlign":"center", "backgroundColor": "#C5E99B", "padding": "7%", "borderRadius": 20}),
    


    dcc.Markdown(
    """
    ___

    ### 世界の感染データ

    European Center for Disease prevention and control

    エクセルデータで毎朝更新

    [https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide](https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide)

    ___

    ### 各都道府県の感染データURL

    #### 東京都

    [オープンデータサイト](https://catalog.data.metro.tokyo.lg.jp/dataset/t000010d0000000068/resource/c2d997db-1450-43fa-8037-ebb11ec28d4c)

    ____

    #### 北海道

    [HTMLに表データで公表](http://www.pref.hokkaido.lg.jp/hf/kth/kak/hasseijoukyou.htm)


    ___

    #### 愛知県

    [PDFで公表](https://www.pref.aichi.jp/uploaded/attachment/325314.pdf)

    ___

    #### 大阪府

    全てのデータをWordファイルで提供

    Docxファイル、Pythonでは[python-docx](https://pypi.org/project/python-docx/)を使うと簡単にパース出来そう。

    [http://www.pref.osaka.lg.jp/iryo/osakakansensho/corona.html](http://www.pref.osaka.lg.jp/iryo/osakakansensho/corona.html)

    ___ 

    #### 京都府

    ウェブページ上に発生件数と年齢などの情報を掲載している

    [https://www.pref.kyoto.jp/kentai/news/novelcoronavirus.html](https://www.pref.kyoto.jp/kentai/news/novelcoronavirus.html)

    """
    , style={"fontSize": 20, "padding": "5%", "paddingTop": 0}
)

], style=memo_style)




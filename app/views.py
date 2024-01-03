from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext

from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
from plotly.graph_objs import Scatter

import pandas as pd
import numpy as np
import json

import yfinance as yf
import datetime as dt
import qrcode

from .models import Project

from sklearn.linear_model import LinearRegression
from sklearn import preprocessing, model_selection, svm
import concurrent.futures
import requests
from sklearn.preprocessing import MinMaxScaler
from yahoo_fin import stock_info

from plotly.subplots import make_subplots
import sys
sys.path.append("/app/AttenLayer.py")

from app.AttenLayer import *


print("Available GPUs:", tf.config.list_physical_devices('GPU'))
print("Available CPUs:", tf.config.list_physical_devices('CPU'))
# The Home page when Server loads up
def index(request):
    # ================================================= Left Card Plot =========================================================
    # Here we use yf.download function
    data = yf.download(
        # passes the ticker
        tickers=['AAPL', 'AMZN', 'QCOM', 'META', 'NVDA', 'JPM'],
        group_by = 'ticker',
        threads=True, # Set thread value to true
        # used for access data[ticker]
        period='12mo',
        interval='1d'
    )
    data.reset_index(level=0, inplace=True)
    fig_left = go.Figure()
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['AAPL']['Adj Close'], name="AAPL")
            )
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['AMZN']['Adj Close'], name="AMZN")
            )
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['QCOM']['Adj Close'], name="QCOM")
            )
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['META']['Adj Close'], name="META")
            )
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['NVDA']['Adj Close'], name="NVDA")
            )
    fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['JPM']['Adj Close'], name="JPM")
            )
    fig_left.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
    plot_div_left = plot(fig_left, auto_open=False, output_type='div')

    # ================================================ To show recent stocks ==============================================
    # df1 = yf.download(tickers = 'AAPL', period='2d', interval='1d')
    df2 = yf.download(tickers = 'AMZN', period='2d', interval='1d')
    df3 = yf.download(tickers = 'GOOGL', period='2d', interval='1d')
    df4 = yf.download(tickers = 'UBER', period='2d', interval='1d')
    df5 = yf.download(tickers = 'TSLA', period='2d', interval='1d')
    df6 = yf.download(tickers = 'TWTR', period='2d', interval='1d')
    df7 = yf.download(tickers = 'QCOM', period='2d', interval='1d')
    df8 = yf.download(tickers = 'META', period='2d', interval='1d')
    df9 = yf.download(tickers = 'NVDA', period='2d', interval='1d')
    df10 = yf.download(tickers = 'JPM', period='2d', interval='1d')

    # df1.insert(0, "Ticker", "AAPL")
    df2.insert(0, "Ticker", "AMZN")
    df3.insert(0, "Ticker", "GOOGL")
    df4.insert(0, "Ticker", "UBER")
    df5.insert(0, "Ticker", "TSLA")
    df6.insert(0, "Ticker", "TWTR")
    df7.insert(0, "Ticker", "QCOM")
    df8.insert(0, "Ticker", "META")
    df9.insert(0, "Ticker", "NVDA")
    df10.insert(0, "Ticker", "JPM")
    df = pd.concat([df2, df3, df4, df5, df6, df7, df8, df9, df10], axis=0)
    df.reset_index(level=0, inplace=True)
    df.columns = ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Adj_Close', 'Volume']
    convert_dict = {'Date': object}
    df = df.astype(convert_dict)
    df.drop('Date', axis=1, inplace=True)
    json_records = df.reset_index().to_json(orient ='records')
    recent_stocks = []
    recent_stocks = json.loads(json_records)
    stocks = []
    for index in range(len(recent_stocks)):
        if(index!=len(recent_stocks)-1):
            if(recent_stocks[index]['Ticker']==recent_stocks[index+1]['Ticker']):
                stocks.append(recent_stocks[index+1])

    # ========================================== Page Render section =====================================================
    return render(request, 'index.html', {
        'plot_div_left': plot_div_left,
        'recent_stocks': stocks
    })
def login(request):
    return render(request, 'login.html', {})
def search(request):
    return render(request, 'search.html', {})
def ticker(request):

    # ================================================= Load Ticker Table ================================================
    ticker_df = pd.read_csv('app/Data/new_tickers.csv')
    json_ticker = ticker_df.reset_index().to_json(orient ='records')
    ticker_list = []
    ticker_list = json.loads(json_ticker)
    return render(request, 'ticker.html', {
        'ticker_list': ticker_list
    })
def searchTicker(request):
    if request.method == 'POST':
        # Lấy dữ liệu từ form sau khi người dùng gửi nó đi
        search_query = request.POST.get('search_query', '')
        # Gọi API với dữ liệu từ form
        api_url = f'https://serverltmnc.onrender.com/ticker/{search_query}'
        try:
            # Thực hiện yêu cầu GET hoặc POST (tùy thuộc vào API)
            response = requests.post(api_url)
            # Xử lý dữ liệu từ API response ở đây
            api_data = response.json()
            api_url_detail = f'https://serverltmnc.onrender.com/infoticker/{api_data.get("Tickers", [])[0].get("_id")}'
            # Thực hiện yêu cầu GET hoặc POST (tùy thuộc vào API)
            response_detail = requests.post(api_url_detail)
            # Xử lý dữ liệu từ API response ở đây
            api_data_detail = response_detail.json()

            try:
                ticker_value = api_data.get('Tickers', [])[0].get('symbol').upper()
                df = yf.download(tickers=ticker_value, period='1d', interval='1m')
                print("Downloaded ticker = {} successfully".format(ticker_value))
            except:
                return render(request, 'API_Down.html', {})
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'], name='market data'))
            fig.update_layout(
                title='{} live share price evolution'.format(ticker_value),
                yaxis_title='Stock Price (USD per Shares)')
            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=15, label="15m", step="minute", stepmode="backward"),
                        dict(count=45, label="45m", step="minute", stepmode="backward"),
                        dict(count=1, label="HTD", step="hour", stepmode="todate"),
                        dict(count=3, label="3h", step="hour", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            )
            fig.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
            plot_div = plot(fig, auto_open=False, output_type='div')

            # ================================================= Center Plot =========================================================
            # Here we use yf.download function
            data = yf.download(
                # passes the ticker
                tickers=[ticker_value],
                group_by='ticker',
                threads=True,  # Set thread value to true
                # used for access data[ticker]
                period='12mo',
                interval='1d'
            )
            data.reset_index(level=0, inplace=True)
            fig_left = go.Figure()
            fig_left.add_trace(
                go.Scatter(x=data['Date'], y=data['Adj Close'], name=ticker_value)
            )
            fig_left.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
            plot_div_left = plot(fig_left, auto_open=False, output_type='div')

            return render(request, 'viewsearch.html', {
                '_id': api_data.get('Tickers', [])[0].get('_id'),
                'symbol': api_data.get('Tickers', [])[0].get('symbol'),
                'companyName': api_data.get('Tickers', [])[0].get('companyName'),
                'industrys': api_data.get('Tickers', [])[0].get('industry'),
                'phoneNumber': api_data.get('Tickers', [])[0].get('phoneNumber'),
                'fax': api_data.get('Tickers', [])[0].get('fax'),
                'email': api_data.get('Tickers', [])[0].get('email'),
                'website': api_data.get('Tickers', [])[0].get('website'),
                'legalRepresentation': api_data.get('Tickers', [])[0].get('legalRepresentation'),
                'details': api_data.get('Tickers', [])[0].get('details'),
                "status": api_data.get('Tickers', [])[0].get('status'),
                "tax_id": api_data.get('Tickers', [])[0].get('tax_id'),
                "GPTL": api_data.get('Tickers', [])[0].get('GPTL'),
                "dateGPTL": api_data.get('Tickers', [])[0].get('dateGPTL'),
                "GPKD": api_data.get('Tickers', [])[0].get('GPKD'),
                "dateGPKD": api_data.get('Tickers', [])[0].get('dateGPKD'),
                "InfoTickers": api_data_detail.get('InfoTickers', []),
                'plot_div': plot_div,
                'plot_div_left': plot_div_left,
            })
        except requests.exceptions.RequestException as e:
            print(f"Error calling API: {e}")
            return HttpResponse("Error calling API")
    else:
        # Xử lý dữ liệu từ GET request ở đây nếu cần thiết
        # ...
        return render(request, 'search.html')

# Function to compile and train a model
def compile_and_train_model(model, X_train, y_train, X_valid, y_valid):
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4), loss='mean_squared_error', metrics=['mae'])
    model.fit(X_train, y_train, batch_size=64, epochs=10, validation_data=(X_valid, y_valid))

# Function to train a model and return it
def train_model(model, X_train, y_train, X_valid, y_valid):
    compile_and_train_model(model, X_train, y_train, X_valid, y_valid)
    return model

# Function for model prediction
def predict_prices(model, X_test, num_steps, number_of_days):
    predicted_prices_scaled = []
    for _ in range(number_of_days):
        predicted_price_scaled = model.predict(X_test)
        predicted_prices_scaled.append(predicted_price_scaled[0, 0])
        X_test = np.roll(X_test, -1)
        X_test[0, -1, 0] = predicted_price_scaled[0, 0]
    return predicted_prices_scaled

# Function for plotting
def plot_stock_predictions(combined_df, title):
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=combined_df['Date'], y=combined_df['Price'], mode='lines+markers'))
    fig.update_xaxes(
        rangeslider_visible=True,
        showgrid=True,
        gridwidth=1,
        gridcolor='gray',
        tickangle=45,
        tickmode='auto',
        nticks=10,
        tickformat="%b %d\n%Y"
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='gray',
        tickangle=0,
        tickformat="$.2f"
    )
    fig.update_layout(
        title=title,
        xaxis_title='Date',
        yaxis_title='Stock Price',
        paper_bgcolor="#f0f0f0",
        plot_bgcolor="#f0f0f0",
        font=dict(color="black"),
        legend=dict(orientation="h", y=1.1, x=0.5),
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return plot(fig, auto_open=False, output_type='div')

# The Predict Function to implement Machine Learning as well as Plotting
def predict(request, ticker_value, number_of_days):
    try:
        # ticker_value = request.POST.get('ticker')
        ticker_value = ticker_value.upper()
        df = yf.download(tickers = ticker_value, period='1d', interval='1m')
        print("Downloaded ticker = {} successfully".format(ticker_value))
    except:
        return render(request, 'API_Down.html', {})
    try:
        # number_of_days = request.POST.get('days')
        number_of_days = int(number_of_days)
    except:
        return render(request, 'Invalid_Days_Format.html', {})
    Valid_Ticker = [
"A","AA","AAC","AACG","AACIW","AADI","AAIC","AAIN","AAL","AAMC","AAME","AAN","AAOI","AAON","AAP","AAPL","AAQC","AAT","AATC","AAU","AAWW","AB","ABB","ABBV","ABC","ABCB","ABCL","ABCM","ABEO","ABEV","ABG","ABIO","ABM","ABMD","ABNB","ABOS","ABR","ABSI","ABST","ABT","ABTX","ABUS","ABVC","AC","ACA","ACAB","ACAD","ACAQ","ACAXR","ACB","ACBA","ACC","ACCD","ACCO","ACEL","ACER","ACET","ACEV","ACEVW","ACGL","ACGLN","ACGLO","ACH","ACHC","ACHL","ACHR","ACHV","ACI","ACII","ACIU","ACIW","ACKIT","ACLS","ACLX","ACM","ACMR","ACN","ACNB","ACON","ACOR","ACP","ACQR","ACQRU","ACR","ACRE","ACRS","ACRX","ACST","ACT","ACTD","ACTDW","ACTG","ACU","ACV","ACVA","ACXP","ADAG","ADALW","ADAP","ADBE","ADC","ADCT","ADER","ADES","ADEX","ADGI","ADI","ADIL","ADM","ADMA","ADMP","ADN","ADNT","ADNWW","ADP","ADPT","ADRA","ADRT","ADSE","ADSEW","ADSK","ADT","ADTH","ADTN","ADTX","ADUS","ADV","ADVM","ADX","ADXN","AE","AEAC","AEACW","AEAE","AEAEW","AEE","AEF","AEFC","AEG","AEHAW","AEHL","AEHR","AEI","AEIS","AEL","AEM","AEMD","AENZ","AEO","AEP","AEPPZ","AER","AERC","AERI","AES","AESC","AESE","AEVA","AEY","AEYE","AEZS","AFAQ","AFAR","AFB","AFBI","AFCG","AFG","AFGB","AFGC","AFGD","AFGE","AFIB","AFL","AFMD","AFRI","AFRIW","AFRM","AFT","AFTR","AFYA","AG","AGAC","AGBAR","AGCB","AGCO","AGD","AGE","AGEN","AGFS","AGFY","AGGR","AGI","AGIL","AGILW","AGIO","AGL","AGLE","AGM","AGMH","AGNC","AGNCM","AGNCN","AGNCO","AGNCP","AGO","AGR","AGRI","AGRO","AGRX","AGS","AGTC","AGTI","AGX","AGYS","AHCO","AHG","AHH","AHI","AHPA","AHPI","AHRNW","AHT","AI","AIB","AIC","AIF","AIG","AIH","AIHS","AIKI","AIM","AIMAW","AIMC","AIN","AINC","AINV","AIO","AIP","AIR","AIRC","AIRG","AIRI","AIRS","AIRT","AIRTP","AIT","AIU","AIV","AIZ","AIZN","AJG","AJRD","AJX","AJXA","AKA","AKAM","AKAN","AKBA","AKICU","AKR","AKRO","AKTS","AKTX","AKU","AKUS","AKYA","AL","ALB","ALBO","ALC","ALCC","ALCO","ALDX","ALE","ALEC","ALEX","ALF","ALFIW","ALG","ALGM","ALGN","ALGS","ALGT","ALHC","ALIM","ALIT","ALJJ","ALK","ALKS","ALKT","ALL","ALLE","ALLG","ALLK","ALLO","ALLR","ALLT","ALLY","ALNA","ALNY","ALORW","ALOT","ALPA","ALPN","ALPP","ALR","ALRM","ALRN","ALRS","ALSA","ALSAR","ALSAU","ALSAW","ALSN","ALT","ALTG","ALTO","ALTR","ALTU","ALTUU","ALTUW","ALV","ALVO","ALVR","ALX","ALXO","ALYA","ALZN","AM","AMAL","AMAM","AMAO","AMAOW","AMAT","AMBA","AMBC","AMBO","AMBP","AMC","AMCI","AMCR","AMCX","AMD","AME","AMED","AMEH","AMG","AMGN","AMH","AMK","AMKR","AMLX","AMN","AMNB","AMOT","AMOV","AMP","AMPE","AMPG","AMPH","AMPI","AMPL","AMPS","AMPY","AMR","AMRC","AMRK","AMRN","AMRS","AMRX","AMS","AMSC","AMSF","AMST","AMSWA","AMT","AMTB","AMTD","AMTI","AMTX","AMWD","AMWL","AMX","AMYT","AMZN","AN","ANAB","ANAC","ANDE","ANEB","ANET","ANF","ANGH","ANGHW","ANGI","ANGN","ANGO","ANIK","ANIP","ANIX","ANNX","ANPC","ANSS","ANTE","ANTX","ANVS","ANY","ANZU","ANZUW","AOD","AOGO","AOMR","AON","AORT","AOS","AOSL","AOUT","AP","APA","APAC","APACW","APAM","APCX","APD","APDN","APEI","APEN","APG","APGB","APH","API","APLD","APLE","APLS","APLT","APM","APMIU","APO","APOG","APP","APPF","APPH","APPHW","APPN","APPS","APRE","APRN","APT","APTM","APTO","APTV","APTX","APVO","APWC","APXI","APYX","AQB","AQMS","AQN","AQNA","AQNB","AQNU","AQST","AQUA","AR","ARAV","ARAY","ARBE","ARBEW","ARBK","ARBKL","ARC","ARCB","ARCC","ARCE","ARCH","ARCK","ARCKW","ARCO","ARCT","ARDC","ARDS","ARDX","ARE","AREB","AREC","AREN","ARES","ARGD","ARGO","ARGU","ARGUU","ARGUW","ARGX","ARHS","ARI","ARIS","ARIZW","ARKO","ARKOW","ARKR","ARL","ARLO","ARLP","ARMK","ARMP","ARNC","AROC","AROW","ARQQ","ARQQW","ARQT","ARR","ARRWU","ARRWW","ARRY","ARTE","ARTEW","ARTL","ARTNA","ARTW","ARVL","ARVN","ARW","ARWR","ASA","ASAI","ASAN","ASAQ","ASAX","ASAXU","ASB","ASC","ASCAU","ASCB","ASCBR","ASG","ASGI","ASGN","ASH","ASIX","ASLE","ASLN","ASM","ASMB","ASML","ASND","ASNS","ASO","ASPA","ASPC","ASPCU","ASPCW","ASPN","ASPS","ASPU","ASR","ASRT","ASRV","ASTC","ASTE","ASTL","ASTLW","ASTR","ASTS","ASTSW","ASUR","ASX","ASXC","ASYS","ASZ","ATA","ATAI","ATAQ","ATAX","ATC","ATCO","ATCX","ATEC","ATEN","ATER","ATEX","ATGE","ATHA","ATHE","ATHM","ATHX","ATI","ATIF","ATIP","ATKR","ATLC","ATLCL","ATLCP","ATLO","ATNF","ATNFW","ATNI","ATNM","ATNX","ATO","ATOM","ATOS","ATR","ATRA","ATRC","ATRI","ATRO","ATSG","ATTO","ATUS","ATVC","ATVCU","ATVI","ATXI","ATXS","ATY","AU","AUB","AUBAP","AUBN","AUD","AUDC","AUGX","AUID","AUMN","AUPH","AUR","AURA","AURC","AUROW","AUS","AUST","AUTL","AUTO","AUUD","AUVI","AUY","AVA","AVAC","AVAH","AVAL","AVAN","AVAV","AVB","AVCO","AVCT","AVCTW","AVD","AVDL","AVDX","AVEO","AVGO","AVGOP","AVGR","AVID","AVIR","AVK","AVLR","AVNS","AVNT","AVNW","AVO","AVPT","AVPTW","AVRO","AVT","AVTE","AVTR","AVTX","AVXL","AVY","AVYA","AWF","AWH","AWI","AWK","AWP","AWR","AWRE","AWX","AX","AXAC","AXDX","AXGN","AXL","AXLA","AXNX","AXON","AXP","AXR","AXS","AXSM","AXTA","AXTI","AXU","AY","AYI","AYLA","AYRO","AYTU","AYX","AZ","AZEK","AZN","AZO","AZPN","AZRE","AZTA","AZUL","AZYO","AZZ","B","BA","BABA","BAC","BACA","BAFN","BAH","BAK","BALL","BALY","BAM","BAMH","BAMI","BAMR","BANC","BAND","BANF","BANFP","BANR","BANX","BAOS","BAP","BARK","BASE","BATL","BATRA","BATRK","BAX","BB","BBAI","BBAR","BBBY","BBCP","BBD","BBDC","BBDO","BBGI","BBI","BBIG","BBIO","BBLG","BBLN","BBN","BBQ","BBSI","BBU","BBUC","BBVA","BBW","BBWI","BBY","BC","BCAB","BCAC","BCACU","BCACW","BCAN","BCAT","BCBP","BCC","BCDA","BCDAW","BCE","BCEL","BCH","BCLI","BCML","BCO","BCOR","BCOV","BCOW","BCPC","BCRX","BCS","BCSA","BCSAW","BCSF","BCTX","BCTXW","BCV","BCX","BCYC","BDC","BDJ","BDL","BDN","BDSX","BDTX","BDX","BDXB","BE","BEAM","BEAT","BECN","BEDU","BEEM","BEKE","BELFA","BELFB","BEN","BENE","BENER","BENEW","BEP","BEPC","BEPH","BEPI","BERY","BEST","BFAC","BFAM","BFC","BFH","BFI","BFIIW","BFIN","BFK","BFLY","BFRI","BFRIW","BFS","BFST","BFZ","BG","BGB","BGCP","BGFV","BGH","BGI","BGNE","BGR","BGRY","BGRYW","BGS","BGSF","BGSX","BGT","BGX","BGXX","BGY","BH","BHAC","BHACU","BHAT","BHB","BHC","BHE","BHF","BHFAL","BHFAM","BHFAN","BHFAO","BHFAP","BHG","BHIL","BHK","BHLB","BHP","BHR","BHSE","BHSEW","BHV","BHVN","BIDU","BIG","BIGC","BIGZ","BIIB","BILI","BILL","BIMI","BIO","BIOC","BIOL","BIOR","BIOSW","BIOT","BIOTU","BIOTW","BIOX","BIP","BIPC","BIPH","BIPI","BIRD","BIT","BITF","BIVI","BJ","BJDX","BJRI","BK","BKCC","BKD","BKE","BKEP","BKEPP","BKH","BKI","BKKT","BKN","BKNG","BKR","BKSC","BKSY","BKT","BKTI","BKU","BKYI","BL","BLBD","BLBX","BLCM","BLCO","BLCT","BLD","BLDE","BLDEW","BLDP","BLDR","BLE","BLEU","BLEUU","BLEUW","BLFS","BLFY","BLI","BLIN","BLK","BLKB","BLMN","BLND","BLNG","BLNGW","BLNK","BLNKW","BLPH","BLRX","BLSA","BLTE","BLTS","BLTSW","BLU","BLUA","BLUE","BLW","BLX","BLZE","BMA","BMAC","BMAQ","BMAQR","BMBL","BME","BMEA","BMEZ","BMI","BMO","BMRA","BMRC","BMRN","BMTX","BMY","BNED","BNFT","BNGO","BNL","BNOX","BNR","BNRG","BNS","BNSO","BNTC","BNTX","BNY","BOAC","BOAS","BOC","BODY","BOE","BOH","BOKF","BOLT","BON","BOOM","BOOT","BORR","BOSC","BOTJ","BOWL","BOX","BOXD","BOXL","BP","BPAC","BPMC","BPOP","BPOPM","BPRN","BPT","BPTH","BPTS","BPYPM","BPYPN","BPYPO","BPYPP","BQ","BR","BRAC","BRACR","BRAG","BRBR","BRBS","BRC","BRCC","BRCN","BRDG","BRDS","BREZ","BREZR","BREZW","BRFH","BRFS","BRG","BRID","BRIV","BRIVW","BRKHU","BRKL","BRKR","BRLI","BRLT","BRMK","BRN","BRO","BROG","BROS","BRP","BRPM","BRPMU","BRPMW","BRQS","BRSP","BRT","BRTX","BRW","BRX","BRY","BRZE","BSAC","BSBK","BSBR","BSET","BSFC","BSGA","BSGAR","BSGM","BSIG","BSKY","BSKYW","BSL","BSM","BSMX","BSQR","BSRR","BST","BSTZ","BSVN","BSX","BSY","BTA","BTAI","BTB","BTBD","BTBT","BTCM","BTCS","BTCY","BTG","BTI","BTMD","BTMDW","BTN","BTO","BTOG","BTRS","BTT","BTTR","BTTX","BTU","BTWN","BTWNU","BTWNW","BTX","BTZ","BUD","BUI","BUR","BURL","BUSE","BV","BVH","BVN","BVS","BVXV","BW","BWA","BWAC","BWACW","BWAQR","BWAY","BWB","BWC","BWCAU","BWEN","BWFG","BWG","BWMN","BWMX","BWNB","BWSN","BWV","BWXT","BX","BXC","BXMT","BXMX","BXP","BXRX","BXSL","BY","BYD","BYFC","BYM","BYN","BYND","BYRN","BYSI","BYTS","BYTSW","BZ","BZFD","BZFDW","BZH","BZUN","C","CAAP","CAAS","CABA","CABO","CAC","CACC","CACI","CADE","CADL","CAE","CAF","CAG","CAH","CAJ","CAKE","CAL","CALA","CALB","CALM","CALT","CALX","CAMP","CAMT","CAN","CANF","CANG","CANO","CAPD","CAPL","CAPR","CAR","CARA","CARE","CARG","CARR","CARS","CARV","CASA","CASH","CASI","CASS","CASY","CAT","CATC","CATO","CATY","CB","CBAN","CBAT","CBAY","CBD","CBFV","CBH","CBIO","CBL","CBNK","CBOE","CBRE","CBRG","CBRL","CBSH","CBT","CBTX","CBU","CBZ","CC","CCAP","CCB","CCBG","CCCC","CCCS","CCD","CCEL","CCEP","CCF","CCI","CCJ","CCK","CCL","CCLP","CCM","CCNC","CCNE","CCNEP","CCO","CCOI","CCRD","CCRN","CCS","CCSI","CCU","CCV","CCVI","CCXI","CCZ","CD","CDAK","CDAY","CDE","CDEV","CDLX","CDMO","CDNA","CDNS","CDR","CDRE","CDRO","CDTX","CDW","CDXC","CDXS","CDZI","CDZIP","CE","CEA","CEAD","CEADW","CECE","CEE","CEG","CEI","CEIX","CELC","CELH","CELU","CELZ","CEM","CEMI","CEN","CENN","CENQW","CENT","CENTA","CENX","CEPU","CEQP","CERE","CERS","CERT","CET","CETX","CETXP","CEV","CEVA","CF","CFB","CFBK","CFFE","CFFI","CFFN","CFG","CFIV","CFIVW","CFLT","CFMS","CFR","CFRX","CFSB","CFVI","CFVIW","CG","CGA","CGABL","CGAU","CGBD","CGC","CGEM","CGEN","CGNT","CGNX","CGO","CGRN","CGTX","CHAA","CHCI","CHCO","CHCT","CHD","CHDN","CHE","CHEA","CHEF","CHEK","CHGG","CHH","CHI","CHK","CHKEL","CHKEW","CHKEZ","CHKP","CHMG","CHMI","CHN","CHNG","CHNR","CHPT","CHRA","CHRB","CHRD","CHRS","CHRW","CHS","CHSCL","CHSCM","CHSCN","CHSCO","CHSCP","CHT","CHTR","CHUY","CHW","CHWA","CHWAW","CHWY","CHX","CHY","CI","CIA","CIB","CIDM","CIEN","CIF","CIFR","CIFRW","CIG","CIGI","CIH","CII","CIIGW","CIK","CIM","CINC","CINF","CING","CINT","CIO","CION","CIR","CISO","CITEW","CIVB","CIVI","CIX","CIXX","CIZN","CJJD","CKPT","CKX","CL","CLAQW","CLAR","CLAS","CLAYU","CLB","CLBK","CLBS","CLBT","CLBTW","CLDT","CLDX","CLEU","CLF","CLFD","CLGN","CLH","CLIM","CLIR","CLLS","CLM","CLMT","CLNE","CLNN","CLOV","CLPR","CLPS","CLPT","CLR","CLRB","CLRO","CLS","CLSD","CLSK","CLSN","CLST","CLVR","CLVRW","CLVS","CLVT","CLW","CLWT","CLX","CLXT","CM","CMA","CMAX","CMAXW","CMBM","CMC","CMCA","CMCL","CMCM","CMCO","CMCSA","CMCT","CME","CMG","CMI","CMLS","CMMB","CMP","CMPO","CMPOW","CMPR","CMPS","CMPX","CMRA","CMRAW","CMRE","CMRX","CMS","CMSA","CMSC","CMSD","CMT","CMTG","CMTL","CMU","CNA","CNC","CNCE","CND","CNDB","CNDT","CNET","CNEY","CNF","CNFRL","CNHI","CNI","CNK","CNM","CNMD","CNNB","CNNE","CNO","CNOB","CNOBP","CNP","CNQ","CNR","CNS","CNSL","CNSP","CNTA","CNTB","CNTG","CNTQ","CNTQW","CNTX","CNTY","CNVY","CNX","CNXA","CNXC","CNXN","CO","COCO","COCP","CODA","CODI","CODX","COE","COF","COFS","COGT","COHN","COHU","COIN","COKE","COLB","COLD","COLI","COLIU","COLIW","COLL","COLM","COMM","COMP","COMS","COMSP","COMSW","CONN","CONX","CONXW","COO","COOK","COOL","COOLU","COOP","COP","CORR","CORS","CORT","CORZ","CORZW","COSM","COST","COTY","COUP","COUR","COVA","COVAU","COVAW","COWN","COWNL","CP","CPA","CPAC","CPAR","CPARU","CPARW","CPB","CPE","CPF","CPG","CPHC","CPHI","CPIX","CPK","CPLP","CPNG","CPOP","CPRI","CPRT","CPRX","CPS","CPSH","CPSI","CPSS","CPT","CPTK","CPTN","CPTNW","CPUH","CPZ","CQP","CR","CRAI","CRBP","CRBU","CRC","CRCT","CRDF","CRDL","CRDO","CREC","CREG","CRESW","CRESY","CREX","CRF","CRGE","CRGY","CRH","CRHC","CRI","CRIS","CRK","CRKN","CRL","CRM","CRMD","CRMT","CRNC","CRNT","CRNX","CRON","CROX","CRS","CRSP","CRSR","CRT","CRTD","CRTDW","CRTO","CRTX","CRU","CRUS","CRVL","CRVS","CRWD","CRWS","CRXT","CRXTW","CS","CSAN","CSBR","CSCO","CSCW","CSGP","CSGS","CSII","CSIQ","CSL","CSPI","CSQ","CSR","CSSE","CSSEN","CSSEP","CSTE","CSTL","CSTM","CSTR","CSV","CSWC","CSWI","CSX","CTAQ","CTAS","CTBB","CTBI","CTDD","CTEK","CTG","CTGO","CTHR","CTIB","CTIC","CTKB","CTLP","CTLT","CTMX","CTO","CTOS","CTR","CTRA","CTRE","CTRM","CTRN","CTS","CTSH","CTSO","CTT","CTV","CTVA","CTXR","CTXRW","CTXS","CUBA","CUBE","CUBI","CUE","CUEN","CUK","CULL","CULP","CURI","CURO","CURV","CUTR","CUZ","CVAC","CVBF","CVCO","CVCY","CVE","CVEO","CVET","CVGI","CVGW","CVI","CVII","CVLG","CVLT","CVLY","CVM","CVNA","CVR","CVRX","CVS","CVT","CVV","CVX","CW","CWAN","CWBC","CWBR","CWCO","CWEN","CWH","CWK","CWST","CWT","CX","CXAC","CXDO","CXE","CXH","CXM","CXW","CYAN","CYBE","CYBN","CYBR","CYCC","CYCCP","CYCN","CYD","CYH","CYN","CYRN","CYRX","CYT","CYTH","CYTK","CYTO","CYXT","CZNC","CZOO","CZR","CZWI","D","DAC","DADA","DAIO","DAKT","DAL","DALN","DAN","DAO","DAOO","DAOOU","DAOOW","DAR","DARE","DASH","DATS","DAVA","DAVE","DAVEW","DAWN","DB","DBD","DBGI","DBI","DBL","DBRG","DBTX","DBVT","DBX","DC","DCBO","DCF","DCFC","DCFCW","DCGO","DCGOW","DCI","DCO","DCOM","DCOMP","DCP","DCPH","DCRD","DCRDW","DCT","DCTH","DD","DDD","DDF","DDI","DDL","DDOG","DDS","DDT","DE","DEA","DECA","DECK","DEI","DELL","DEN","DENN","DEO","DESP","DEX","DFFN","DFH","DFIN","DFP","DFS","DG","DGHI","DGICA","DGII","DGLY","DGNU","DGX","DH","DHACW","DHBC","DHBCU","DHC","DHCAU","DHCNI","DHCNL","DHF","DHHC","DHI","DHIL","DHR","DHT","DHX","DHY","DIAX","DIBS","DICE","DIN","DINO","DIOD","DIS","DISA","DISH","DIT","DK","DKL","DKNG","DKS","DLA","DLB","DLCA","DLHC","DLNG","DLO","DLPN","DLR","DLTH","DLTR","DLX","DLY","DM","DMA","DMAC","DMB","DMF","DMLP","DMO","DMRC","DMS","DMTK","DNA","DNAA","DNAB","DNAC","DNAD","DNAY","DNB","DNLI","DNMR","DNN","DNOW","DNP","DNUT","DNZ","DO","DOC","DOCN","DOCS","DOCU","DOGZ","DOLE","DOMA","DOMO","DOOO","DOOR","DORM","DOUG","DOV","DOW","DOX","DOYU","DPG","DPRO","DPSI","DPZ","DQ","DRCT","DRD","DRE","DRH","DRI","DRIO","DRMA","DRMAW","DRQ","DRRX","DRTS","DRTSW","DRTT","DRUG","DRVN","DS","DSAC","DSACU","DSACW","DSEY","DSGN","DSGR","DSGX","DSKE","DSL","DSM","DSP","DSS","DSU","DSWL","DSX","DT","DTB","DTC","DTE","DTEA","DTF","DTG","DTIL","DTM","DTOCW","DTP","DTSS","DTST","DTW","DUK","DUKB","DUNE","DUNEW","DUO","DUOL","DUOT","DV","DVA","DVAX","DVN","DWAC","DWACU","DWACW","DWIN","DWSN","DX","DXC","DXCM","DXF","DXLG","DXPE","DXR","DXYN","DY","DYAI","DYFN","DYN","DYNT","DZSI","E","EA","EAC","EACPW","EAD","EAF","EAI","EAR","EARN","EAST","EAT","EB","EBACU","EBAY","EBC","EBET","EBF","EBIX","EBMT","EBON","EBR","EBS","EBTC","EC","ECAT","ECC","ECCC","ECCW","ECCX","ECF","ECL","ECOM","ECOR","ECPG","ECVT","ED","EDAP","EDBL","EDBLW","EDD","EDF","EDI","EDIT","EDN","EDNC","EDR","EDRY","EDSA","EDTK","EDTX","EDU","EDUC","EE","EEA","EEFT","EEIQ","EEX","EFC","EFL","EFOI","EFR","EFSC","EFSCP","EFT","EFTR","EFX","EGAN","EGBN","EGF","EGHT","EGIO","EGLE","EGLX","EGO","EGP","EGRX","EGY","EH","EHAB","EHC","EHI","EHTH","EIC","EICA","EIG","EIGR","EIM","EIX","EJH","EKSO","EL","ELA","ELAN","ELAT","ELBM","ELC","ELDN","ELEV","ELF","ELMD","ELOX","ELP","ELS","ELSE","ELTK","ELV","ELVT","ELY","ELYM","ELYS","EM","EMAN","EMBC","EMBK","EMBKW","EMCF","EMD","EME","EMF","EMKR","EML","EMLD","EMN","EMO","EMP","EMR","EMWP","EMX","ENB","ENBA","ENCP","ENCPW","ENDP","ENER","ENERW","ENFN","ENG","ENIC","ENJ","ENJY","ENJYW","ENLC","ENLV","ENO","ENOB","ENOV","ENPC","ENPH","ENR","ENS","ENSC","ENSG","ENSV","ENTA","ENTFW","ENTG","ENTX","ENTXW","ENV","ENVA","ENVB","ENVX","ENX","ENZ","EOCW","EOD","EOG","EOI","EOLS","EOS","EOSE","EOSEW","EOT","EP","EPAC","EPAM","EPC","EPD","EPHY","EPHYU","EPHYW","EPIX","EPM","EPR","EPRT","EPSN","EPWR","EPZM","EQ","EQBK","EQC","EQD","EQH","EQHA","EQIX","EQNR","EQOS","EQR","EQRX","EQRXW","EQS","EQT","EQX","ERAS","ERC","ERES","ERESU","ERF","ERH","ERIC","ERIE","ERII","ERJ","ERO","ERYP","ES","ESAB","ESAC","ESCA","ESE","ESEA","ESGR","ESGRO","ESGRP","ESI","ESLT","ESMT","ESNT","ESOA","ESPR","ESQ","ESRT","ESS","ESSA","ESSC","ESSCW","ESTA","ESTC","ESTE","ET","ETAC","ETACW","ETB","ETD","ETG","ETJ","ETN","ETNB","ETO","ETON","ETR","ETRN","ETSY","ETTX","ETV","ETW","ETWO","ETX","ETY","EUCR","EURN","EVA","EVAX","EVBG","EVBN","EVC","EVCM","EVER","EVEX","EVF","EVFM","EVG","EVGN","EVGO","EVGOW","EVGR","EVH","EVI","EVK","EVLO","EVLV","EVM","EVN","EVO","EVOJ","EVOJU","EVOJW","EVOK","EVOP","EVR","EVRG","EVRI","EVT","EVTC","EVTL","EVTV","EVV","EW","EWBC","EWCZ","EWTX","EXAI","EXAS","EXC","EXD","EXEL","EXFY","EXG","EXK","EXLS","EXN","EXP","EXPD","EXPE","EXPI","EXPO","EXPR","EXR","EXTN","EXTR","EYE","EYEN","EYES","EYPT","EZFL","EZGO","EZPW","F","FA","FACA","FACT","FAF","FAM","FAMI","FANG","FANH","FARM","FARO","FAST","FAT","FATBB","FATBP","FATE","FATH","FATP","FAX","FBC","FBHS","FBIO","FBIOP","FBIZ","FBK","FBMS","FBNC","FBP","FBRT","FBRX","FC","FCAP","FCAX","FCBC","FCCO","FCEL","FCF","FCFS","FCN","FCNCA","FCNCO","FCNCP","FCO","FCPT","FCRD","FCRX","FCT","FCUV","FCX","FDBC","FDEU","FDMT","FDP","FDS","FDUS","FDX","FE","FEAM","FEDU","FEI","FELE","FEMY","FEN","FENC","FENG","FEO","FERG","FET","FEXD","FEXDR","FF","FFA","FFBC","FFC","FFHL","FFIC","FFIE","FFIEW","FFIN","FFIV","FFNW","FFWM","FGB","FGBI","FGBIP","FGEN","FGF","FGFPP","FGI","FGIWW","FGMC","FHB","FHI","FHN","FHS","FHTX","FIAC","FIACW","FIBK","FICO","FIF","FIGS","FINM","FINMW","FINS","FINV","FINW","FIS","FISI","FISV","FITB","FITBI","FITBO","FITBP","FIVE","FIVN","FIX","FIXX","FIZZ","FKWL","FL","FLAC","FLACU","FLAG","FLC","FLEX","FLGC","FLGT","FLIC","FLL","FLME","FLNC","FLNG","FLNT","FLO","FLR","FLS","FLT","FLUX","FLWS","FLXS","FLYA","FLYW","FMAO","FMBH","FMC","FMIV","FMIVW","FMN","FMNB","FMS","FMTX","FMX","FMY","FN","FNA","FNB","FNCB","FNCH","FND","FNF","FNGR","FNHC","FNKO","FNLC","FNV","FNVTW","FNWB","FNWD","FOA","FOCS","FOF","FOLD","FONR","FOR","FORA","FORD","FORG","FORM","FORR","FORTY","FOSL","FOSLL","FOUN","FOUNU","FOUNW","FOUR","FOX","FOXA","FOXF","FOXW","FPAC","FPAY","FPF","FPH","FPI","FPL","FR","FRA","FRAF","FRBA","FRBK","FRBN","FRBNW","FRC","FRD","FREE","FREQ","FREY","FRG","FRGAP","FRGE","FRGI","FRGT","FRHC","FRLAW","FRLN","FRME","FRMEP","FRO","FROG","FRON","FRONU","FRPH","FRPT","FRSG","FRSGW","FRSH","FRST","FRSX","FRT","FRWAW","FRXB","FSBC","FSBW","FSD","FSEA","FSFG","FSI","FSK","FSLR","FSLY","FSM","FSNB","FSP","FSR","FSRD","FSRDW","FSRX","FSS","FSSI","FSSIW","FST","FSTR","FSTX","FSV","FT","FTAA","FTAI","FTAIN","FTAIO","FTAIP","FTCH","FTCI","FTCV","FTCVU","FTCVW","FTDR","FTEK","FTEV","FTF","FTFT","FTHM","FTHY","FTI","FTK","FTNT","FTPA","FTPAU","FTRP","FTS","FTV","FTVI","FUBO","FUL","FULC","FULT","FULTP","FUN","FUNC","FUND","FURY","FUSB","FUSN","FUTU","FUV","FVAM","FVCB","FVIV","FVRR","FWBI","FWONA","FWONK","FWP","FWRD","FWRG","FXCO","FXCOR","FXLV","FXNC","FYBR","G","GAB","GABC","GACQ","GACQW","GAIA","GAIN","GAINN","GALT","GAM","GAMB","GAMC","GAME","GAN","GANX","GAPA","GAQ","GASS","GATEW","GATO","GATX","GAU","GB","GBAB","GBBK","GBBKR","GBBKW","GBCI","GBDC","GBIO","GBL","GBLI","GBNH","GBOX","GBR","GBRGR","GBS","GBT","GBTG","GBX","GCBC","GCI","GCMG","GCMGW","GCO","GCP","GCV","GD","GDDY","GDEN","GDL","GDNRW","GDO","GDOT","GDRX","GDS","GDV","GDYN","GE","GECC","GECCM","GECCN","GECCO","GEEX","GEEXU","GEF","GEG","GEGGL","GEHI","GEL","GENC","GENE","GENI","GEO","GEOS","GER","GERN","GES","GET","GEVO","GF","GFAI","GFAIW","GFF","GFGD","GFI","GFL","GFLU","GFS","GFX","GGAA","GGAAU","GGAAW","GGAL","GGB","GGE","GGG","GGMC","GGN","GGR","GGROW","GGT","GGZ","GH","GHAC","GHACU","GHC","GHG","GHIX","GHL","GHLD","GHM","GHRS","GHSI","GHY","GIB","GIC","GIFI","GIGM","GIII","GIIX","GIIXW","GIL","GILD","GILT","GIM","GIPR","GIPRW","GIS","GIW","GIWWW","GKOS","GL","GLAD","GLBE","GLBL","GLBS","GLDD","GLDG","GLEE","GLG","GLHA","GLLIR","GLLIW","GLMD","GLNG","GLO","GLOB","GLOP","GLP","GLPG","GLPI","GLQ","GLRE","GLS","GLSI","GLSPT","GLT","GLTO","GLU","GLUE","GLV","GLW","GLYC","GM","GMAB","GMBL","GMBLP","GMDA","GME","GMED","GMFI","GMGI","GMRE","GMS","GMTX","GMVD","GNAC","GNACU","GNE","GNFT","GNK","GNL","GNLN","GNPX","GNRC","GNS","GNSS","GNT","GNTX","GNTY","GNUS","GNW","GO","GOAC","GOBI","GOCO","GOED","GOEV","GOEVW","GOF","GOGL","GOGO","GOL","GOLD","GOLF","GOOD","GOODN","GOODO","GOOG","GOOGL","GOOS","GORO","GOSS","GOTU","GOVX","GP","GPAC","GPACU","GPACW","GPC","GPCO","GPCOW","GPI","GPJA","GPK","GPL","GPMT","GPN","GPOR","GPP","GPRE","GPRK","GPRO","GPS","GRAB","GRABW","GRAY","GRBK","GRC","GRCL","GRCYU","GREE","GREEL","GRF","GRFS","GRIL","GRIN","GRMN","GRNA","GRNAW","GRNQ","GROM","GROMW","GROV","GROW","GROY","GRPH","GRPN","GRTS","GRTX","GRVI","GRVY","GRWG","GRX","GS","GSAQ","GSAQW","GSAT","GSBC","GSBD","GSEV","GSHD","GSIT","GSK","GSL","GSLD","GSM","GSMG","GSQB","GSRM","GSRMU","GSUN","GSV","GT","GTAC","GTACU","GTBP","GTE","GTEC","GTES","GTH","GTHX","GTIM","GTLB","GTLS","GTN","GTPB","GTX","GTXAP","GTY","GUG","GURE","GUT","GVA","GVCIU","GVP","GWH","GWRE","GWRS","GWW","GXII","GXO","H","HA","HAAC","HAACU","HAACW","HAE","HAFC","HAIA","HAIAU","HAIAW","HAIN","HAL","HALL","HALO","HAPP","HARP","HAS","HASI","HAYN","HAYW","HBAN","HBANM","HBANP","HBB","HBCP","HBI","HBIO","HBM","HBNC","HBT","HCA","HCAR","HCARU","HCARW","HCAT","HCC","HCCI","HCDI","HCDIP","HCDIW","HCDIZ","HCI","HCIC","HCICU","HCII","HCKT","HCM","HCNE","HCNEU","HCNEW","HCP","HCSG","HCTI","HCVI","HCWB","HD","HDB","HDSN","HE","HEAR","HEES","HEI","HELE","HEP","HEPA","HEPS","HEQ","HERA","HERAU","HERAW","HES","HESM","HEXO","HFBL","HFFG","HFRO","HFWA","HGBL","HGEN","HGLB","HGTY","HGV","HHC","HHGCW","HHLA","HHS","HI","HIBB","HIE","HIG","HIGA","HIHO","HII","HIII","HIL","HILS","HIMS","HIMX","HIO","HIPO","HITI","HIVE","HIW","HIX","HL","HLBZ","HLBZW","HLF","HLG","HLGN","HLI","HLIO","HLIT","HLLY","HLMN","HLNE","HLT","HLTH","HLVX","HLX","HMC","HMCO","HMCOU","HMLP","HMN","HMNF","HMPT","HMST","HMTV","HMY","HNGR","HNI","HNNA","HNNAZ","HNRA","HNRG","HNST","HNVR","HNW","HOFT","HOFV","HOFVW","HOG","HOLI","HOLX","HOMB","HON","HONE","HOOD","HOOK","HOPE","HOTH","HOUR","HOUS","HOV","HOVNP","HOWL","HP","HPE","HPF","HPI","HPK","HPKEW","HPP","HPQ","HPS","HPX","HQH","HQI","HQL","HQY","HR","HRB","HRI","HRL","HRMY","HROW","HROWL","HRT","HRTG","HRTX","HRZN","HSAQ","HSBC","HSC","HSCS","HSDT","HSIC","HSII","HSKA","HSON","HST","HSTM","HSTO","HSY","HT","HTA","HTAQ","HTBI","HTBK","HTCR","HTD","HTFB","HTFC","HTGC","HTGM","HTH","HTHT","HTIA","HTIBP","HTLD","HTLF","HTLFP","HTOO","HTPA","HTY","HTZ","HTZWW","HUBB","HUBG","HUBS","HUDI","HUGE","HUGS","HUIZ","HUM","HUMA","HUMAW","HUN","HURC","HURN","HUSA","HUT","HUYA","HVBC","HVT","HWBK","HWC","HWCPZ","HWKN","HWKZ","HWM","HXL","HY","HYB","HYFM","HYI","HYLN","HYMC","HYMCW","HYMCZ","HYPR","HYRE","HYT","HYW","HYZN","HYZNW","HZN","HZNP","HZO","HZON","IAA","IAC","IACC","IAE","IAF","IAG","IART","IAS","IAUX","IBA","IBCP","IBER","IBEX","IBIO","IBKR","IBM","IBN","IBOC","IBP","IBRX","IBTX","ICAD","ICCC","ICCH","ICCM","ICD","ICE","ICFI","ICHR","ICL","ICLK","ICLR","ICMB","ICNC","ICPT","ICUI","ICVX","ID","IDA","IDAI","IDBA","IDCC","IDE","IDEX","IDN","IDR","IDRA","IDT","IDW","IDXX","IDYA","IE","IEA","IEAWW","IEP","IESC","IEX","IFBD","IFF","IFN","IFRX","IFS","IGA","IGAC","IGACW","IGC","IGD","IGI","IGIC","IGICW","IGMS","IGR","IGT","IGTAR","IH","IHD","IHG","IHIT","IHRT","IHS","IHT","IHTA","IIF","III","IIII","IIIIU","IIIIW","IIIN","IIIV","IIM","IINN","IINNW","IIPR","IIVI","IIVIP","IKNA","IKT","ILMN","ILPT","IMAB","IMAC","IMAQ","IMAQR","IMAQW","IMAX","IMBI","IMBIL","IMCC","IMCR","IMGN","IMGO","IMH","IMKTA","IMMP","IMMR","IMMX","IMNM","IMO","IMOS","IMPL","IMPP","IMPPP","IMPX","IMRA","IMRN","IMRX","IMTE","IMTX","IMUX","IMV","IMVT","IMXI","INAQ","INBK","INBKZ","INBX","INCR","INCY","INDB","INDI","INDIW","INDO","INDP","INDT","INFA","INFI","INFN","INFU","INFY","ING","INGN","INGR","INKA","INKAW","INKT","INM","INMB","INMD","INN","INNV","INO","INOD","INPX","INSE","INSG","INSI","INSM","INSP","INST","INSW","INT","INTA","INTC","INTEW","INTG","INTR","INTT","INTU","INTZ","INUV","INVA","INVE","INVH","INVO","INVZ","INVZW","INZY","IOBT","IONM","IONQ","IONR","IONS","IOSP","IOT","IOVA","IP","IPA","IPAR","IPAXW","IPDN","IPG","IPGP","IPHA","IPI","IPOD","IPOF","IPSC","IPVA","IPVF","IPVI","IPW","IPWR","IPX","IQ","IQI","IQMD","IQMDW","IQV","IR","IRBT","IRDM","IREN","IRIX","IRL","IRM","IRMD","IRNT","IRRX","IRS","IRT","IRTC","IRWD","IS","ISAA","ISD","ISDR","ISEE","ISIG","ISLE","ISLEW","ISO","ISPC","ISPO","ISPOW","ISR","ISRG","ISSC","ISTR","ISUN","IT","ITCB","ITCI","ITGR","ITHX","ITHXU","ITHXW","ITI","ITIC","ITOS","ITP","ITQ","ITRG","ITRI","ITRM","ITRN","ITT","ITUB","ITW","IVA","IVAC","IVC","IVCAU","IVCAW","IVCB","IVCBW","IVCP","IVDA","IVH","IVR","IVT","IVZ","IX","IXHL","IZEA","J","JACK","JAGX","JAKK","JAMF","JAN","JANX","JAQCW","JAZZ","JBGS","JBHT","JBI","JBL","JBLU","JBSS","JBT","JCE","JCI","JCIC","JCICW","JCSE","JCTCF","JD","JEF","JELD","JEMD","JEQ","JFIN","JFR","JFU","JG","JGGCU","JGGCW","JGH","JHAA","JHG","JHI","JHS","JHX","JILL","JJSF","JKHY","JKS","JLL","JLS","JMACW","JMIA","JMM","JMSB","JNCE","JNJ","JNPR","JOAN","JOB","JOBY","JOE","JOF","JOFF","JOFFU","JOFFW","JOUT","JPC","JPI","JPM","JPS","JPT","JQC","JRI","JRO","JRS","JRSH","JRVR","JSD","JSM","JSPR","JSPRW","JT","JUGG","JUGGW","JUN","JUPW","JUPWW","JVA","JWAC","JWEL","JWN","JWSM","JXN","JYAC","JYNT","JZXN","K","KACL","KACLR","KAHC","KAI","KAII","KAIR","KAL","KALA","KALU","KALV","KALWW","KAMN","KAR","KARO","KAVL","KB","KBAL","KBH","KBNT","KBNTW","KBR","KC","KCGI","KD","KDNY","KDP","KE","KELYA","KEN","KEP","KEQU","KERN","KERNW","KEX","KEY","KEYS","KF","KFFB","KFRC","KFS","KFY","KGC","KHC","KIDS","KIIIW","KIM","KIND","KINS","KINZ","KINZU","KINZW","KIO","KIQ","KIRK","KKR","KKRS","KLAC","KLAQ","KLAQU","KLIC","KLR","KLTR","KLXE","KMB","KMDA","KMF","KMI","KMPB","KMPH","KMPR","KMT","KMX","KN","KNBE","KNDI","KNOP","KNSA","KNSL","KNTE","KNTK","KNX","KO","KOD","KODK","KOF","KOP","KOPN","KORE","KOS","KOSS","KPLT","KPLTW","KPRX","KPTI","KR","KRBP","KRC","KREF","KRG","KRKR","KRMD","KRNL","KRNLU","KRNT","KRNY","KRO","KRON","KROS","KRP","KRT","KRTX","KRUS","KRYS","KSCP","KSM","KSPN","KSS","KT","KTB","KTCC","KTF","KTH","KTN","KTOS","KTRA","KTTA","KUKE","KULR","KURA","KVHI","KVSC","KW","KWAC","KWR","KXIN","KYCH","KYMR","KYN","KZIA","KZR","L","LAAA","LAB","LABP","LAC","LAD","LADR","LAKE","LAMR","LANC","LAND","LANDM","LANDO","LARK","LASR","LAUR","LAW","LAZ","LAZR","LAZY","LBAI","LBC","LBPH","LBRDA","LBRDK","LBRDP","LBRT","LBTYA","LBTYK","LC","LCA","LCAA","LCFY","LCFYW","LCI","LCID","LCII","LCNB","LCTX","LCUT","LCW","LDHA","LDHAW","LDI","LDOS","LDP","LE","LEA","LEAP","LECO","LEDS","LEE","LEG","LEGA","LEGH","LEGN","LEJU","LEN","LEO","LESL","LEU","LEV","LEVI","LEXX","LFAC","LFACU","LFACW","LFC","LFG","LFLY","LFLYW","LFMD","LFMDP","LFST","LFT","LFTR","LFUS","LFVN","LGAC","LGHL","LGHLW","LGI","LGIH","LGL","LGMK","LGND","LGO","LGST","LGSTW","LGTO","LGTOW","LGV","LGVN","LH","LHC","LHCG","LHDX","LHX","LI","LIAN","LIBYW","LICY","LIDR","LIDRW","LIFE","LII","LILA","LILAK","LILM","LILMW","LIN","LINC","LIND","LINK","LION","LIONW","LIQT","LITB","LITE","LITM","LITT","LIVE","LIVN","LIXT","LIZI","LJAQ","LJAQU","LJPC","LKCO","LKFN","LKQ","LL","LLAP","LLL","LLY","LMACA","LMACU","LMACW","LMAO","LMAT","LMB","LMDX","LMFA","LMND","LMNL","LMNR","LMPX","LMST","LMT","LNC","LND","LNDC","LNFA","LNG","LNN","LNSR","LNT","LNTH","LNW","LOAN","LOB","LOCL","LOCO","LODE","LOGC","LOGI","LOMA","LOOP","LOPE","LOTZ","LOTZW","LOV","LOVE","LOW","LPCN","LPG","LPI","LPL","LPLA","LPRO","LPSN","LPTH","LPTX","LPX","LQDA","LQDT","LRCX","LRFC","LRMR","LRN","LSAK","LSCC","LSEA","LSEAW","LSF","LSI","LSPD","LSTR","LSXMA","LSXMB","LSXMK","LTBR","LTC","LTCH","LTCHW","LTH","LTHM","LTRN","LTRPA","LTRX","LTRY","LTRYW","LU","LUCD","LULU","LUMN","LUMO","LUNA","LUNG","LUV","LUXA","LUXAU","LUXAW","LVAC","LVACW","LVLU","LVO","LVOX","LVRA","LVS","LVTX","LW","LWLG","LX","LXEH","LXFR","LXP","LXRX","LXU","LYB","LYEL","LYFT","LYG","LYL","LYLT","LYRA","LYT","LYTS","LYV","LZ","LZB","M","MA","MAA","MAAQ","MAAQW","MAC","MACA","MACAU","MACAW","MACC","MACK","MAG","MAIN","MAN","MANH","MANT","MANU","MAPS","MAPSW","MAQC","MAQCU","MAQCW","MAR","MARA","MARK","MARPS","MAS","MASI","MASS","MAT","MATV","MATW","MATX","MAV","MAX","MAXN","MAXR","MBAC","MBCN","MBI","MBII","MBIN","MBINN","MBINO","MBINP","MBIO","MBNKP","MBOT","MBRX","MBTCR","MBTCU","MBUU","MBWM","MC","MCAA","MCAAW","MCAC","MCB","MCBC","MCBS","MCD","MCFT","MCG","MCHP","MCHX","MCI","MCK","MCLD","MCN","MCO","MCR","MCRB","MCRI","MCS","MCW","MCY","MD","MDB","MDC","MDGL","MDGS","MDGSW","MDIA","MDJH","MDLZ","MDNA","MDRR","MDRX","MDT","MDU","MDV","MDVL","MDWD","MDWT","MDXG","MDXH","ME","MEAC","MEACW","MEC","MED","MEDP","MEDS","MEG","MEGI","MEI","MEIP","MEKA","MELI","MEOA","MEOAW","MEOH","MERC","MESA","MESO","MET","META","METC","METCL","METX","METXW","MF","MFA","MFC","MFD","MFG","MFGP","MFH","MFIN","MFM","MFV","MG","MGA","MGEE","MGF","MGI","MGIC","MGLD","MGM","MGNI","MGNX","MGPI","MGR","MGRB","MGRC","MGRD","MGTA","MGTX","MGU","MGY","MHD","MHF","MHH","MHI","MHK","MHLA","MHLD","MHN","MHNC","MHO","MHUA","MIC","MICS","MICT","MIDD","MIGI","MILE","MIMO","MIN","MIND","MINDP","MINM","MIO","MIR","MIRM","MIRO","MIST","MIT","MITC","MITK","MITO","MITQ","MITT","MIXT","MIY","MKC","MKD","MKFG","MKL","MKSI","MKTW","MKTX","ML","MLAB","MLAC","MLCO","MLI","MLKN","MLM","MLNK","MLP","MLR","MLSS","MLTX","MLVF","MMAT","MMC","MMD","MMI","MMLP","MMM","MMMB","MMP","MMS","MMSI","MMT","MMU","MMX","MMYT","MN","MNDO","MNDT","MNDY","MNKD","MNMD","MNOV","MNP","MNPR","MNRL","MNRO","MNSB","MNSBP","MNSO","MNST","MNTK","MNTS","MNTSW","MNTV","MNTX","MO","MOBQ","MOBQW","MOD","MODD","MODN","MODV","MOFG","MOGO","MOGU","MOH","MOHO","MOLN","MOMO","MON","MONCW","MOR","MORF","MORN","MOS","MOTS","MOV","MOVE","MOXC","MP","MPA","MPAA","MPACR","MPB","MPC","MPLN","MPLX","MPV","MPW","MPWR","MPX","MQ","MQT","MQY","MRAI","MRAM","MRBK","MRC","MRCC","MRCY","MREO","MRIN","MRK","MRKR","MRM","MRNA","MRNS","MRO","MRSN","MRTN","MRTX","MRUS","MRVI","MRVL","MS","MSA","MSAC","MSB","MSBI","MSC","MSCI","MSD","MSDA","MSDAW","MSEX","MSFT","MSGE","MSGM","MSGS","MSI","MSM","MSN","MSPR","MSPRW","MSPRZ","MSTR","MT","MTA","MTAC","MTACW","MTAL","MTB","MTBC","MTBCO","MTBCP","MTC","MTCH","MTCN","MTCR","MTD","MTDR","MTEK","MTEKW","MTEM","MTEX","MTG","MTH","MTLS","MTMT","MTN","MTNB","MTOR","MTP","MTR","MTRN","MTRX","MTRY","MTSI","MTTR","MTVC","MTW","MTX","MTZ","MU","MUA","MUC","MUDS","MUDSW","MUE","MUFG","MUI","MUJ","MULN","MUR","MURFW","MUSA","MUX","MVBF","MVF","MVIS","MVO","MVST","MVSTW","MVT","MWA","MX","MXC","MXCT","MXE","MXF","MXL","MYD","MYE","MYFW","MYGN","MYI","MYMD","MYN","MYNA","MYNZ","MYO","MYOV","MYPS","MYRG","MYSZ","MYTE","NAAC","NAACW","NAAS","NABL","NAC","NAD","NAII","NAK","NAN","NAOV","NAPA","NARI","NAT","NATH","NATI","NATR","NAUT","NAVB","NAVI","NAZ","NBB","NBEV","NBH","NBHC","NBIX","NBN","NBO","NBR","NBRV","NBSE","NBSTW","NBTB","NBTX","NBW","NBXG","NBY","NC","NCA","NCAC","NCACU","NCACW","NCLH","NCMI","NCNA","NCNO","NCR","NCSM","NCTY","NCV","NCZ","NDAC","NDACU","NDACW","NDAQ","NDLS","NDMO","NDP","NDRA","NDSN","NE","NEA","NECB","NEE","NEGG","NEM","NEN","NEO","NEOG","NEON","NEOV","NEP","NEPH","NEPT","NERV","NESR","NESRW","NET","NETI","NEU","NEWP","NEWR","NEWT","NEWTL","NEX","NEXA","NEXI","NEXT","NFBK","NFE","NFG","NFGC","NFJ","NFLX","NFYS","NG","NGC","NGD","NGG","NGL","NGM","NGMS","NGS","NGVC","NGVT","NH","NHC","NHI","NHIC","NHICW","NHS","NHTC","NHWK","NI","NIC","NICE","NICK","NID","NIE","NILE","NIM","NINE","NIO","NIQ","NISN","NIU","NJR","NKE","NKG","NKLA","NKSH","NKTR","NKTX","NKX","NL","NLIT","NLITU","NLITW","NLOK","NLS","NLSN","NLSP","NLSPW","NLTX","NLY","NM","NMAI","NMCO","NMFC","NMG","NMI","NMIH","NML","NMM","NMMC","NMR","NMRD","NMRK","NMS","NMT","NMTC","NMTR","NMZ","NN","NNBR","NNDM","NNI","NNN","NNOX","NNVC","NNY","NOA","NOAC","NOACW","NOAH","NOC","NODK","NOG","NOK","NOM","NOMD","NOTV","NOV","NOVA","NOVN","NOVT","NOW","NPAB","NPCE","NPCT","NPFD","NPK","NPO","NPTN","NPV","NQP","NR","NRACU","NRACW","NRBO","NRC","NRDS","NRDY","NREF","NRG","NRGV","NRGX","NRIM","NRIX","NRK","NRO","NRP","NRSN","NRSNW","NRT","NRUC","NRXP","NRXPW","NRZ","NS","NSA","NSC","NSIT","NSL","NSP","NSPR","NSR","NSS","NSSC","NSTB","NSTG","NSTS","NSYS","NTAP","NTB","NTCO","NTCT","NTES","NTG","NTGR","NTIC","NTIP","NTLA","NTNX","NTR","NTRA","NTRB","NTRBW","NTRS","NTRSO","NTST","NTUS","NTWK","NTZ","NU","NUE","NUO","NURO","NUS","NUTX","NUV","NUVA","NUVB","NUVL","NUW","NUWE","NUZE","NVACR","NVAX","NVCN","NVCR","NVCT","NVDA","NVEC","NVEE","NVEI","NVFY","NVG","NVGS","NVIV","NVMI","NVNO","NVO","NVOS","NVR","NVRO","NVS","NVSA","NVSAU","NVSAW","NVST","NVT","NVTA","NVTS","NVVE","NVVEW","NVX","NWBI","NWE","NWFL","NWG","NWL","NWLI","NWN","NWPX","NWS","NWSA","NX","NXC","NXDT","NXE","NXGL","NXGLW","NXGN","NXJ","NXN","NXP","NXPI","NXPL","NXRT","NXST","NXTC","NXTP","NYC","NYCB","NYMT","NYMTL","NYMTM","NYMTN","NYMTZ","NYMX","NYT","NYXH","NZF","O","OB","OBCI","OBE","OBLG","OBNK","OBSV","OC","OCAX","OCC","OCCI","OCCIO","OCFC","OCFT","OCG","OCGN","OCN","OCSL","OCUL","OCUP","OCX","ODC","ODFL","ODP","ODV","OEC","OEG","OEPW","OEPWW","OESX","OFC","OFG","OFIX","OFLX","OFS","OG","OGE","OGEN","OGI","OGN","OGS","OHI","OHPA","OHPAU","OHPAW","OI","OIA","OII","OIIM","OIS","OKE","OKTA","OKYO","OLB","OLED","OLIT","OLK","OLLI","OLMA","OLN","OLO","OLP","OLPX","OM","OMAB","OMC","OMCL","OMEG","OMER","OMEX","OMF","OMGA","OMI","OMIC","OMQS","ON","ONB","ONBPO","ONBPP","ONCR","ONCS","ONCT","ONCY","ONDS","ONEM","ONEW","ONL","ONON","ONTF","ONTO","ONTX","ONVO","ONYX","ONYXW","OOMA","OP","OPA","OPAD","OPBK","OPCH","OPEN","OPFI","OPGN","OPI","OPINL","OPK","OPNT","OPP","OPRA","OPRT","OPRX","OPT","OPTN","OPTT","OPY","OR","ORA","ORAN","ORC","ORCC","ORCL","ORGN","ORGNW","ORGO","ORGS","ORI","ORIC","ORLA","ORLY","ORMP","ORN","ORRF","ORTX","OSBC","OSCR","OSG","OSH","OSIS","OSK","OSPN","OSS","OST","OSTK","OSTR","OSTRU","OSTRW","OSUR","OSW","OTECW","OTEX","OTIC","OTIS","OTLK","OTLY","OTMO","OTRK","OTRKP","OTTR","OUST","OUT","OVBC","OVID","OVLY","OVV","OWL","OWLT","OXAC","OXACW","OXBR","OXBRW","OXLC","OXLCL","OXLCM","OXLCN","OXLCO","OXLCP","OXLCZ","OXM","OXSQ","OXSQG","OXSQL","OXUS","OXUSW","OXY","OYST","OZ","OZK","OZKAP","PAA","PAAS","PAC","PACB","PACI","PACK","PACW","PACWP","PACX","PACXU","PACXW","PAG","PAGP","PAGS","PAHC","PAI","PALI","PALT","PAM","PANL","PANW","PAQC","PAQCU","PAQCW","PAR","PARA","PARAA","PARAP","PARR","PASG","PATH","PATI","PATK","PAVM","PAVMZ","PAX","PAXS","PAY","PAYA","PAYC","PAYO","PAYS","PAYX","PB","PBA","PBBK","PBF","PBFS","PBFX","PBH","PBHC","PBI","PBLA","PBPB","PBR","PBT","PBTS","PBYI","PCAR","PCB","PCCT","PCF","PCG","PCGU","PCH","PCK","PCM","PCN","PCOR","PCPC","PCQ","PCRX","PCSA","PCSB","PCT","PCTI","PCTTW","PCTY","PCVX","PCX","PCYG","PCYO","PD","PDCE","PDCO","PDD","PDEX","PDFS","PDI","PDLB","PDM","PDO","PDOT","PDS","PDSB","PDT","PEAK","PEAR","PEARW","PEB","PEBK","PEBO","PECO","PED","PEG","PEGA","PEGR","PEGRU","PEGY","PEI","PEN","PENN","PEO","PEP","PEPG","PEPL","PEPLW","PERI","PESI","PETQ","PETS","PETV","PETVW","PETZ","PEV","PFBC","PFC","PFD","PFDR","PFDRW","PFE","PFG","PFGC","PFH","PFHC","PFHD","PFIE","PFIN","PFIS","PFL","PFLT","PFMT","PFN","PFO","PFS","PFSI","PFSW","PFTA","PFTAU","PFX","PFXNL","PG","PGC","PGEN","PGNY","PGP","PGR","PGRE","PGRU","PGRW","PGRWU","PGTI","PGY","PGYWW","PGZ","PH","PHAR","PHAS","PHAT","PHCF","PHD","PHG","PHGE","PHI","PHIC","PHIO","PHK","PHM","PHR","PHT","PHUN","PHUNW","PHVS","PHX","PI","PIAI","PICC","PII","PIII","PIIIW","PIK","PIM","PINC","PINE","PING","PINS","PIPP","PIPR","PIRS","PIXY","PJT","PK","PKBK","PKE","PKG","PKI","PKOH","PKX","PL","PLAB","PLAG","PLAY","PLBC","PLBY","PLCE","PLD","PLG","PLL","PLM","PLMI","PLMIU","PLMIW","PLMR","PLNT","PLOW","PLPC","PLRX","PLSE","PLTK","PLTR","PLUG","PLUS","PLX","PLXP","PLXS","PLYA","PLYM","PM","PMCB","PMD","PME","PMF","PMGM","PMGMW","PML","PMM","PMO","PMT","PMTS","PMVP","PMX","PNACU","PNBK","PNC","PNF","PNFP","PNFPP","PNI","PNM","PNNT","PNR","PNRG","PNT","PNTG","PNTM","PNW","POAI","PODD","POET","POLA","POLY","POND","PONO","PONOW","POOL","POR","PORT","POSH","POST","POW","POWI","POWL","POWRU","POWW","POWWP","PPBI","PPBT","PPC","PPG","PPIH","PPL","PPSI","PPT","PPTA","PRA","PRAA","PRAX","PRBM","PRCH","PRCT","PRDO","PRDS","PRE","PRFT","PRFX","PRG","PRGO","PRGS","PRI","PRIM","PRK","PRLB","PRLD","PRLH","PRM","PRMW","PRO","PROC","PROCW","PROF","PROV","PRPB","PRPC","PRPH","PRPL","PRPO","PRQR","PRS","PRSO","PRSR","PRSRU","PRSRW","PRT","PRTA","PRTG","PRTH","PRTK","PRTS","PRTY","PRU","PRVA","PRVB","PSA","PSAG","PSAGU","PSAGW","PSB","PSEC","PSF","PSFE","PSHG","PSMT","PSN","PSNL","PSNY","PSNYW","PSO","PSPC","PSTG","PSTH","PSTI","PSTL","PSTV","PSTX","PSX","PT","PTA","PTC","PTCT","PTE","PTEN","PTGX","PTIX","PTLO","PTMN","PTN","PTNR","PTON","PTPI","PTR","PTRA","PTRS","PTSI","PTVE","PTY","PUBM","PUCK","PUCKW","PUK","PULM","PUMP","PUYI","PV","PVBC","PVH","PVL","PW","PWFL","PWOD","PWP","PWR","PWSC","PWUPW","PX","PXD","PXLW","PXS","PXSAP","PYCR","PYN","PYPD","PYPL","PYR","PYS","PYT","PYXS","PZC","PZG","PZN","PZZA","QCOM","QCRH","QD","QDEL","QFIN","QFTA","QGEN","QH","QIPT","QK","QLGN","QLI","QLYS","QMCO","QNGY","QNRX","QNST","QQQX","QRHC","QRTEA","QRTEB","QRTEP","QRVO","QS","QSI","QSR","QTEK","QTEKW","QTNT","QTRX","QTT","QTWO","QUAD","QUBT","QUIK","QUMU","QUOT","QURE","QVCC","QVCD","R","RA","RAAS","RACE","RAD","RADA","RADI","RAIL","RAIN","RAM","RAMMU","RAMMW","RAMP","RANI","RAPT","RARE","RAVE","RBA","RBAC","RBB","RBBN","RBCAA","RBCN","RBKB","RBLX","RBOT","RC","RCA","RCAT","RCB","RCC","RCEL","RCFA","RCG","RCHG","RCHGU","RCHGW","RCI","RCII","RCKT","RCKY","RCL","RCLF","RCLFW","RCM","RCMT","RCON","RCOR","RCRT","RCRTW","RCS","RCUS","RDBX","RDBXW","RDCM","RDFN","RDHL","RDI","RDIB","RDN","RDNT","RDUS","RDVT","RDW","RDWR","RDY","RE","REAL","REAX","REE","REEAW","REED","REFI","REFR","REG","REGN","REI","REKR","RELI","RELIW","RELL","RELX","RELY","RENEU","RENEW","RENN","RENT","REPL","REPX","RERE","RES","RETA","RETO","REV","REVB","REVBW","REVEW","REVG","REVH","REVHU","REVHW","REX","REXR","REYN","REZI","RF","RFACW","RFI","RFIL","RFL","RFM","RFMZ","RFP","RGA","RGC","RGCO","RGEN","RGF","RGLD","RGLS","RGNX","RGP","RGR","RGS","RGT","RGTI","RGTIW","RH","RHE","RHI","RHP","RIBT","RICK","RIDE","RIG","RIGL","RILY","RILYG","RILYK","RILYL","RILYM","RILYN","RILYO","RILYP","RILYT","RILYZ","RIO","RIOT","RIV","RIVN","RJF","RKDA","RKLB","RKLY","RKT","RKTA","RL","RLAY","RLGT","RLI","RLJ","RLMD","RLTY","RLX","RLYB","RM","RMAX","RMBI","RMBL","RMBS","RMCF","RMD","RMED","RMGC","RMGCW","RMI","RMM","RMMZ","RMNI","RMO","RMR","RMT","RMTI","RNA","RNAZ","RNDB","RNER","RNERW","RNG","RNGR","RNLX","RNP","RNR","RNST","RNW","RNWK","RNWWW","RNXT","ROAD","ROC","ROCC","ROCGU","ROCK","ROCLU","ROCLW","ROG","ROIC","ROIV","ROIVW","ROK","ROKU","ROL","ROLL","ROLLP","RONI","ROOT","ROP","ROSE","ROSEU","ROSEW","ROSS","ROST","ROVR","RPAY","RPD","RPHM","RPID","RPM","RPRX","RPT","RPTX","RQI","RRBI","RRC","RRGB","RRR","RRX","RS","RSF","RSG","RSI","RSKD","RSLS","RSSS","RSVR","RSVRW","RTL","RTLPO","RTLPP","RTLR","RTX","RUBY","RUN","RUSHA","RUSHB","RUTH","RVAC","RVACU","RVACW","RVLP","RVLV","RVMD","RVNC","RVP","RVPH","RVPHW","RVSB","RVSN","RVT","RWAY","RWLK","RWT","RXDX","RXRX","RXST","RXT","RY","RYAAY","RYAM","RYAN","RYI","RYN","RYTM","RZA","RZB","RZLT","S","SA","SABR","SABRP","SABS","SABSW","SACC","SACH","SAFE","SAFM","SAFT","SAGA","SAGE","SAH","SAI","SAIA","SAIC","SAIL","SAITW","SAL","SALM","SAM","SAMAW","SAMG","SAN","SANA","SAND","SANM","SANW","SAP","SAR","SASI","SASR","SAT","SATL","SATLW","SATS","SAVA","SAVE","SB","SBAC","SBBA","SBCF","SBET","SBEV","SBFG","SBFM","SBFMW","SBGI","SBH","SBI","SBIG","SBII","SBLK","SBNY","SBNYP","SBOW","SBR","SBRA","SBS","SBSI","SBSW","SBT","SBTX","SBUX","SCAQU","SCCB","SCCC","SCCE","SCCF","SCCO","SCD","SCHL","SCHN","SCHW","SCI","SCKT","SCL","SCLE","SCLEU","SCLEW","SCM","SCOA","SCOAW","SCOB","SCOBU","SCOBW","SCOR","SCPH","SCPL","SCPS","SCRM","SCRMW","SCS","SCSC","SCTL","SCU","SCVL","SCWO","SCWX","SCX","SCYX","SD","SDAC","SDACU","SDACW","SDC","SDGR","SDH","SDHY","SDIG","SDPI","SE","SEAC","SEAS","SEAT","SEB","SECO","SEDG","SEE","SEED","SEEL","SEER","SEIC","SELB","SELF","SEM","SEMR","SENEA","SENS","SERA","SES","SESN","SEV","SEVN","SF","SFB","SFBS","SFE","SFET","SFIX","SFL","SFM","SFNC","SFST","SFT","SG","SGA","SGBX","SGC","SGEN","SGFY","SGH","SGHC","SGHL","SGHT","SGIIW","SGLY","SGMA","SGML","SGMO","SGRP","SGRY","SGTX","SGU","SHAC","SHAK","SHBI","SHC","SHCA","SHCAU","SHCR","SHCRW","SHEL","SHEN","SHG","SHI","SHIP","SHLS","SHLX","SHO","SHOO","SHOP","SHPW","SHQA","SHQAU","SHW","SHYF","SI","SIBN","SID","SIDU","SIEB","SIEN","SIER","SIF","SIFY","SIG","SIGA","SIGI","SIGIP","SII","SILC","SILK","SILV","SIMO","SINT","SIOX","SIRE","SIRI","SISI","SITC","SITE","SITM","SIVB","SIVBP","SIX","SJ","SJI","SJIJ","SJIV","SJM","SJR","SJT","SJW","SKE","SKIL","SKIN","SKLZ","SKM","SKT","SKX","SKY","SKYA","SKYH","SKYT","SKYW","SKYX","SLAB","SLAC","SLB","SLCA","SLCR","SLCRW","SLDB","SLDP","SLDPW","SLF","SLG","SLGC","SLGG","SLGL","SLGN","SLHG","SLHGP","SLI","SLM","SLN","SLNH","SLNHP","SLNO","SLP","SLQT","SLRC","SLRX","SLS","SLVM","SLVR","SLVRU","SM","SMAP","SMAPW","SMAR","SMBC","SMBK","SMCI","SMED","SMFG","SMFL","SMFR","SMFRW","SMG","SMHI","SMID","SMIHU","SMIT","SMLP","SMLR","SMM","SMMF","SMMT","SMP","SMPL","SMR","SMRT","SMSI","SMTC","SMTI","SMTS","SMWB","SNA","SNAP","SNAX","SNAXW","SNBR","SNCE","SNCR","SNCRL","SNCY","SND","SNDA","SNDL","SNDR","SNDX","SNES","SNEX","SNFCA","SNGX","SNMP","SNN","SNOA","SNOW","SNP","SNPO","SNPS","SNPX","SNRH","SNRHU","SNRHW","SNSE","SNT","SNTG","SNTI","SNV","SNX","SNY","SO","SOBR","SOFI","SOFO","SOHO","SOHOB","SOHON","SOHOO","SOHU","SOI","SOJC","SOJD","SOJE","SOL","SOLN","SOLO","SON","SOND","SONM","SONN","SONO","SONX","SONY","SOPA","SOPH","SOR","SOS","SOTK","SOUN","SOUNW","SOVO","SP","SPB","SPCB","SPCE","SPE","SPFI","SPG","SPGI","SPGS","SPH","SPI","SPIR","SPKB","SPKBU","SPKBW","SPLK","SPLP","SPNE","SPNS","SPNT","SPOK","SPOT","SPPI","SPR","SPRB","SPRC","SPRO","SPSC","SPT","SPTK","SPTKW","SPTN","SPWH","SPWR","SPXC","SPXX","SQ","SQFT","SQFTP","SQFTW","SQL","SQLLW","SQM","SQNS","SQSP","SQZ","SR","SRAD","SRAX","SRC","SRCE","SRCL","SRDX","SRE","SREA","SREV","SRG","SRGA","SRI","SRL","SRLP","SRNE","SRPT","SRRK","SRSA","SRT","SRTS","SRV","SRZN","SRZNW","SSAA","SSB","SSBI","SSBK","SSD","SSIC","SSKN","SSL","SSNC","SSNT","SSP","SSRM","SSSS","SST","SSTI","SSTK","SSU","SSY","SSYS","ST","STAA","STAB","STAF","STAG","STAR","STBA","STC","STCN","STE","STEM","STEP","STER","STEW","STG","STGW","STIM","STK","STKL","STKS","STLA","STLD","STM","STN","STNE","STNG","STOK","STON","STOR","STR","STRA","STRC","STRCW","STRE","STRL","STRM","STRN","STRNW","STRO","STRR","STRS","STRT","STRY","STSA","STSS","STSSW","STT","STTK","STVN","STWD","STX","STXS","STZ","SU","SUAC","SUI","SUM","SUMO","SUN","SUNL","SUNW","SUP","SUPN","SUPV","SURF","SURG","SURGW","SUZ","SVC","SVFA","SVFAU","SVFAW","SVFD","SVM","SVNAW","SVRA","SVRE","SVT","SVVC","SWAG","SWAV","SWBI","SWCH","SWET","SWETW","SWI","SWIM","SWIR","SWK","SWKH","SWKS","SWN","SWT","SWTX","SWVL","SWVLW","SWX","SWZ","SXC","SXI","SXT","SXTC","SY","SYBT","SYBX","SYF","SYK","SYM","SYN","SYNA","SYNH","SYNL","SYPR","SYRS","SYTA","SYTAW","SYY","SZC","T","TA","TAC","TACT","TAIT","TAK","TAL","TALK","TALKW","TALO","TALS","TANH","TANNI","TANNL","TANNZ","TAOP","TAP","TARA","TARO","TARS","TASK","TAST","TATT","TAYD","TBB","TBBK","TBC","TBCPU","TBI","TBK","TBKCP","TBLA","TBLD","TBLT","TBLTW","TBNK","TBPH","TC","TCBC","TCBI","TCBIO","TCBK","TCBP","TCBPW","TCBS","TCBX","TCDA","TCFC","TCI","TCMD","TCN","TCOM","TCON","TCPC","TCRR","TCRT","TCRX","TCS","TCVA","TCX","TD","TDC","TDCX","TDF","TDG","TDOC","TDS","TDUP","TDW","TDY","TEAF","TEAM","TECH","TECK","TECTP","TEDU","TEF","TEI","TEKK","TEKKU","TEL","TELA","TELL","TELZ","TEN","TENB","TENX","TEO","TER","TERN","TESS","TETC","TETCU","TETCW","TETE","TETEU","TEVA","TEX","TFC","TFFP","TFII","TFSA","TFSL","TFX","TG","TGA","TGAA","TGAN","TGB","TGH","TGI","TGLS","TGNA","TGR","TGS","TGT","TGTX","TGVC","TGVCW","TH","THACW","THC","THCA","THCP","THFF","THG","THM","THMO","THO","THQ","THR","THRM","THRN","THRX","THRY","THS","THTX","THW","THWWW","TIG","TIGO","TIGR","TIL","TILE","TIMB","TINV","TIPT","TIRX","TISI","TITN","TIVC","TIXT","TJX","TK","TKAT","TKC","TKLF","TKNO","TKR","TLGA","TLGY","TLGYW","TLIS","TLK","TLRY","TLS","TLSA","TLYS","TM","TMAC","TMBR","TMC","TMCI","TMCWW","TMDI","TMDX","TME","TMHC","TMKR","TMKRU","TMKRW","TMO","TMP","TMQ","TMST","TMUS","TMX","TNC","TNDM","TNET","TNGX","TNK","TNL","TNON","TNP","TNXP","TNYA","TOI","TOIIW","TOL","TOMZ","TOP","TOPS","TOST","TOUR","TOWN","TPB","TPC","TPG","TPGY","TPH","TPHS","TPIC","TPL","TPR","TPST","TPTA","TPTX","TPVG","TPX","TPZ","TR","TRAQ","TRC","TRCA","TRDA","TREE","TREX","TRGP","TRHC","TRI","TRIB","TRIN","TRIP","TRKA","TRMB","TRMD","TRMK","TRMR","TRN","TRNO","TRNS","TRON","TROO","TROW","TROX","TRP","TRQ","TRS","TRST","TRT","TRTL","TRTN","TRTX","TRU","TRUE","TRUP","TRV","TRVG","TRVI","TRVN","TRX","TS","TSAT","TSBK","TSCO","TSE","TSEM","TSHA","TSI","TSIB","TSLA","TSLX","TSM","TSN","TSP","TSPQ","TSQ","TSRI","TSVT","TT","TTC","TTCF","TTD","TTE","TTEC","TTEK","TTGT","TTI","TTM","TTMI","TTNP","TTOO","TTP","TTSH","TTWO","TU","TUEM","TUFN","TUP","TURN","TUSK","TUYA","TV","TVC","TVE","TVTX","TW","TWI","TWIN","TWKS","TWLO","TWLV","TWN","TWND","TWNI","TWNK","TWO","TWOA","TWOU","TWST","TWTR","TX","TXG","TXMD","TXN","TXRH","TXT","TY","TYDE","TYG","TYL","TYME","TYRA","TZOO","TZPS","TZPSW","U","UA","UAA","UAL","UAMY","UAN","UAVS","UBA","UBCP","UBER","UBFO","UBOH","UBP","UBS","UBSI","UBX","UCBI","UCBIO","UCL","UCTT","UDMY","UDR","UE","UEC","UEIC","UFAB","UFCS","UFI","UFPI","UFPT","UG","UGI","UGIC","UGP","UGRO","UHAL","UHS","UHT","UI","UIHC","UIS","UK","UKOMW","UL","ULBI","ULCC","ULH","ULTA","UMBF","UMC","UMH","UMPQ","UNAM","UNB","UNCY","UNF","UNFI","UNH","UNIT","UNM","UNMA","UNP","UNTY","UNVR","UONE","UONEK","UP","UPC","UPH","UPLD","UPS","UPST","UPTDW","UPWK","URBN","URG","URGN","URI","UROY","USA","USAC","USAK","USAP","USAS","USAU","USB","USCB","USCT","USDP","USEA","USEG","USER","USFD","USIO","USLM","USM","USNA","USPH","USWS","USWSW","USX","UTAA","UTAAW","UTF","UTG","UTHR","UTI","UTL","UTMD","UTME","UTRS","UTSI","UTZ","UUU","UUUU","UVE","UVSP","UVV","UWMC","UXIN","UZD","UZE","UZF","V","VABK","VAC","VACC","VAL","VALE","VALN","VALU","VAPO","VATE","VAXX","VBF","VBIV","VBLT","VBNK","VBTX","VC","VCEL","VCIF","VCKA","VCKAW","VCNX","VCSA","VCTR","VCV","VCXA","VCXAU","VCXAW","VCXB","VCYT","VECO","VECT","VEDU","VEEE","VEEV","VEL","VELO","VELOU","VENA","VENAR","VENAW","VEON","VERA","VERB","VERBW","VERI","VERO","VERU","VERV","VERX","VERY","VET","VEV","VFC","VFF","VFL","VG","VGFC","VGI","VGM","VGR","VGZ","VHAQ","VHC","VHI","VHNAW","VIA","VIAO","VIASP","VIAV","VICI","VICR","VIEW","VIEWW","VIGL","VINC","VINE","VINO","VINP","VIOT","VIPS","VIR","VIRC","VIRI","VIRT","VIRX","VISL","VIST","VITL","VIV","VIVE","VIVK","VIVO","VJET","VKI","VKQ","VKTX","VLAT","VLCN","VLD","VLDR","VLDRW","VLGEA","VLN","VLNS","VLO","VLON","VLRS","VLT","VLTA","VLY","VLYPO","VLYPP","VMAR","VMC","VMCAW","VMD","VMEO","VMGA","VMI","VMO","VMW","VNCE","VNDA","VNET","VNO","VNOM","VNRX","VNT","VNTR","VOC","VOD","VOR","VORB","VORBW","VOXX","VOYA","VPG","VPV","VQS","VRA","VRAR","VRAY","VRCA","VRDN","VRE","VREX","VRM","VRME","VRMEW","VRNA","VRNS","VRNT","VRPX","VRRM","VRSK","VRSN","VRT","VRTS","VRTV","VRTX","VS","VSACW","VSAT","VSCO","VSEC","VSH","VST","VSTA","VSTM","VSTO","VTAQ","VTAQW","VTEX","VTGN","VTIQ","VTIQW","VTN","VTNR","VTOL","VTR","VTRS","VTRU","VTSI","VTVT","VTYX","VUZI","VVI","VVNT","VVOS","VVPR","VVR","VVV","VWE","VWEWW","VXRT","VYGG","VYGR","VYNE","VYNT","VZ","VZIO","VZLA","W","WAB","WABC","WAFD","WAFDP","WAFU","WAL","WALD","WALDW","WARR","WASH","WAT","WATT","WAVC","WAVD","WAVE","WB","WBA","WBD","WBEV","WBS","WBT","WBX","WCC","WCN","WD","WDAY","WDC","WDFC","WDH","WDI","WDS","WE","WEA","WEAV","WEBR","WEC","WEJO","WEJOW","WEL","WELL","WEN","WERN","WES","WETF","WEX","WEYS","WF","WFC","WFCF","WFG","WFRD","WGO","WH","WHD","WHF","WHG","WHLM","WHLR","WHLRD","WHLRP","WHR","WIA","WILC","WIMI","WINA","WING","WINT","WINVR","WIRE","WISA","WISH","WIT","WIW","WIX","WK","WKEY","WKHS","WKME","WKSP","WKSPW","WLDN","WLFC","WLK","WLKP","WLMS","WLY","WM","WMB","WMC","WMG","WMK","WMPN","WMS","WMT","WNC","WNEB","WNNR","WNS","WNW","WOLF","WOOF","WOR","WORX","WOW","WPC","WPCA","WPCB","WPM","WPP","WPRT","WQGA","WRAP","WRB","WRBY","WRE","WRK","WRLD","WRN","WSBC","WSBCP","WSBF","WSC","WSFS","WSM","WSO","WSR","WST","WSTG","WTBA","WTER","WTFC","WTFCM","WTFCP","WTI","WTM","WTRG","WTRH","WTS","WTT","WTTR","WTW","WU","WULF","WVE","WVVI","WVVIP","WW","WWAC","WWACW","WWD","WWE","WWR","WWW","WY","WYNN","WYY","X","XAIR","XBIO","XBIT","XCUR","XEL","XELA","XELAP","XELB","XENE","XERS","XFIN","XFINW","XFLT","XFOR","XGN","XHR","XIN","XL","XLO","XM","XMTR","XNCR","XNET","XOM","XOMA","XOMAO","XOMAP","XOS","XOSWW","XP","XPAX","XPAXW","XPDB","XPDBU","XPDBW","XPEL","XPER","XPEV","XPL","XPO","XPOA","XPOF","XPON","XPRO","XRAY","XRTX","XRX","XSPA","XTLB","XTNT","XXII","XYF","XYL","Y","YALA","YCBD","YELL","YELP","YETI","YEXT","YGMZ","YI","YJ","YMAB","YMM","YMTX","YORW","YOTAR","YOTAW","YOU","YPF","YQ","YRD","YSG","YTEN","YTPG","YTRA","YUM","YUMC","YVR","YY","Z","ZBH","ZBRA","ZCMD","ZD","ZDGE","ZEAL","ZEN","ZENV","ZEPP","ZEST","ZETA","ZEUS","ZEV","ZG","ZGN","ZH","ZI","ZIM","ZIMV","ZING","ZINGW","ZION","ZIONL","ZIONO","ZIONP","ZIP","ZIVO","ZKIN","ZLAB","ZM","ZNH","ZNTL","ZOM","ZS","ZT","ZTEK","ZTO","ZTR","ZTS","ZUMZ","ZUO","ZVIA","ZVO","ZWRK","ZWS","ZY","ZYME","ZYNE","ZYXI"
]
    if ticker_value not in Valid_Ticker:
        return render(request, 'Invalid_Ticker.html', {})
    if number_of_days < 0:
        return render(request, 'Negative_Days.html', {})
    if number_of_days > 365:
        return render(request, 'Overflow_days.html', {})
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'], name = 'market data'))
    fig.update_layout(
                        title='{} live share price evolution'.format(ticker_value),
                        yaxis_title='Stock Price (USD per Shares)')
    fig.update_xaxes(
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
        dict(count=15, label="15m", step="minute", stepmode="backward"),
        dict(count=45, label="45m", step="minute", stepmode="backward"),
        dict(count=1, label="HTD", step="hour", stepmode="todate"),
        dict(count=3, label="3h", step="hour", stepmode="backward"),
        dict(count=1, label="1d", step="day", stepmode="backward"),  # Thêm chế độ xem 1 ngày
        dict(count=7, label="1w", step="day", stepmode="backward"),  # Thêm chế độ xem 1 tuần
        dict(count=1, label="1m", step="month", stepmode="backward"),  # Thêm chế độ xem 1 tháng
        dict(step="all")
        ])
        )
    )
    fig.update_layout(paper_bgcolor="#14151b", plot_bgcolor="#14151b", font_color="white")
    plot_div = plot(fig, auto_open=False, output_type='div')
    # ========================================== Machine Learning ==========================================
    # Download stock data
    try:
        df = yf.download(tickers=ticker_value, period='12mo', interval='1h')
    except Exception as e:
        # Handle the error, e.g., print a message or provide a default dataset
        print(f"Error downloading data: {e}")
        df = yf.download(tickers='AAPL', period='12mo', interval='1h')

    # Extract 'Adj Close' prices
    prices = df['Adj Close'].values.reshape(-1, 1)

    # Scale the data
    scaler = MinMaxScaler(feature_range=(-2, 2))
    prices_scaled = scaler.fit_transform(prices)

    # Prepare training data
    num_steps = 5
    X_train, y_train = [], []
    for i in range(num_steps, len(prices_scaled) - number_of_days):
        X_train.append(prices_scaled[i - num_steps:i, 0])
        y_train.append(prices_scaled[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train).reshape(len(y_train), 1)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Split the data into training and validation sets
    split_index = int(len(X_train) * 0.8)
    X_train, X_valid, y_train, y_valid = X_train[:split_index], X_train[split_index:], y_train[:split_index], y_train[split_index:]
    
    # Build models
    model_lstm = build_model_LSTM(X_train.shape[1], X_train.shape[-1])
    model_bilstm = build_model_BiLSTM(X_train.shape[1], X_train.shape[-1])
    model_cnn_bilstm = build_model_CNN_BiLSTM(X_train.shape, X_train.shape[-1])

    # Use concurrent futures to parallelize training
    with concurrent.futures.ThreadPoolExecutor() as executor:
        lstm_future = executor.submit(train_model, model_lstm, X_train, y_train, X_valid, y_valid)
        bilstm_future = executor.submit(train_model, model_bilstm, X_train, y_train, X_valid, y_valid)
        cnn_bilstm_future = executor.submit(train_model, model_cnn_bilstm, tf.expand_dims(X_train, axis=-1), y_train, tf.expand_dims(X_valid, axis=-1), y_valid)

    # Get the trained models
    model_lstm = lstm_future.result()
    model_bilstm = bilstm_future.result()
    model_cnn_bilstm = cnn_bilstm_future.result()

    # Prepare test data for all three models
    X_test = prices_scaled[-num_steps:]
    X_test = X_test.reshape(1, num_steps, 1)

    # Predict future prices for all three models
    predicted_prices_lstm = predict_prices(model_lstm, X_test, num_steps, number_of_days)
    predicted_prices_bilstm = predict_prices(model_bilstm, X_test, num_steps, number_of_days)
    predicted_prices_cnn_bilstm = predict_prices(model_cnn_bilstm, tf.expand_dims(X_test, axis=-1), num_steps, number_of_days)

    # Inverse transform predicted prices to original scale for all three models
    predicted_prices_lstm = scaler.inverse_transform(np.array(predicted_prices_lstm).reshape(-1, 1))
    predicted_prices_bilstm = scaler.inverse_transform(np.array(predicted_prices_bilstm).reshape(-1, 1))
    predicted_prices_cnn_bilstm = scaler.inverse_transform(np.array(predicted_prices_cnn_bilstm).reshape(-1, 1))

    # Generate future dates for all three models
    future_dates_lstm = [df.index[-1] + pd.DateOffset(days=i) for i in range(1, number_of_days + 1)]
    future_dates_bilstm = [df.index[-1] + pd.DateOffset(days=i) for i in range(1, number_of_days + 1)]
    future_dates_cnn_bilstm = [df.index[-1] + pd.DateOffset(days=i) for i in range(1, number_of_days + 1)]

    # Combine original data and predictions for all three models
    combined_prices_lstm = np.concatenate((prices, predicted_prices_lstm))
    combined_prices_bilstm = np.concatenate((prices, predicted_prices_bilstm))
    combined_prices_cnn_bilstm = np.concatenate((prices, predicted_prices_cnn_bilstm))

    # Combine dates for all three models
    combined_dates_lstm = np.concatenate((df.index, future_dates_lstm))
    combined_dates_bilstm = np.concatenate((df.index, future_dates_bilstm))
    combined_dates_cnn_bilstm = np.concatenate((df.index, future_dates_cnn_bilstm))

    # Create DataFrames for the combined data for all three models
    combined_df_lstm = pd.DataFrame({'Date': combined_dates_lstm, 'Price': combined_prices_lstm.flatten()})
    combined_df_bilstm = pd.DataFrame({'Date': combined_dates_bilstm, 'Price': combined_prices_bilstm.flatten()})
    combined_df_cnn_bilstm = pd.DataFrame({'Date': combined_dates_cnn_bilstm, 'Price': combined_prices_cnn_bilstm.flatten()})
    
    # Generate plot divisions for all three models
    plot_div_pred_lstm = plot_stock_predictions(combined_df_lstm, title='LSTM Predictions')
    plot_div_pred_bilstm = plot_stock_predictions(combined_df_bilstm, title='BiLSTM Predictions')
    plot_div_pred_cnn_bilstm = plot_stock_predictions(combined_df_cnn_bilstm, title='CNN + BiLSTM Predictions')
    
    # Hiển thị thông tin mã chứng khoán 
    ticker = pd.read_csv('app/Data/Tickers.csv')
    to_search = ticker_value
    ticker.columns = ['Symbol', 'Name', 'Last_Sale', 'Net_Change', 'Percent_Change', 'Market_Cap',
                    'Country', 'IPO_Year', 'Volume', 'Sector', 'Industry']
    for i in range(0,ticker.shape[0]):
        if ticker.Symbol[i] == to_search:
            Symbol = ticker.Symbol[i]
            Name = ticker.Name[i]
            Last_Sale = ticker.Last_Sale[i]
            Net_Change = ticker.Net_Change[i]
            Percent_Change = ticker.Percent_Change[i]
            Market_Cap = ticker.Market_Cap[i]
            Country = ticker.Country[i]
            IPO_Year = ticker.IPO_Year[i]
            Volume = ticker.Volume[i]
            Sector = ticker.Sector[i]
            Industry = ticker.Industry[i]
            break
        # Lấy thông tin về cổ phiếu
    stock_info_data = stock_info.get_quote_table(ticker_value)
    # Hiển thị các giá trị cụ thể bạn quan tâm
    values_of_interest = ['1y Target Est', '52 Week Range', 'Ask', 'Avg. Volume', 'Beta (5Y Monthly)', 'Bid', "Day's Range", 'EPS (TTM)', 'Earnings Date', 'Ex-Dividend Date', 'Forward Dividend & Yield', 'Market Cap', 'Open', 'PE Ratio (TTM)', 'Previous Close', 'Quote Price', 'Volume']
    info_ticker = []
    for key in values_of_interest:
        info_ticker.append(stock_info_data.get(key, 'N/A'))
    # ========================================== Page Render section ==========================================
    return render(request, "result.html", context={ 'plot_div': plot_div,
                                                'confidence' : "",
                                                'forecast': "",
                                                'ticker_value':ticker_value,
                                                'number_of_days':number_of_days,
                                                'plot_div_pred_lstm':plot_div_pred_lstm,
                                                'plot_div_pred_bilstm':plot_div_pred_bilstm,
                                                'plot_div_pred_cnn_bilstm':plot_div_pred_cnn_bilstm,
                                                'Symbol':Symbol,
                                                'Name':Name,
                                                'Last_Sale':Last_Sale,
                                                'Net_Change':Net_Change,
                                                'Percent_Change':Percent_Change,
                                                'Market_Cap':Market_Cap,
                                                'Country':Country,
                                                'IPO_Year':IPO_Year,
                                                'Volume':Volume,
                                                'Sector':Sector,
                                                'Industry':Industry,
                                                })

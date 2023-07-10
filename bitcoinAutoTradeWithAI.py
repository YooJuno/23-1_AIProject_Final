import time
import pyupbit
import datetime
import schedule
from prophet import Prophet

access = "VTJBxRRNXuS6lxzJsPGWlSC2xRvk8d7jGKAztoP1"
secret = "369wva72AmEcbLQjDOLQaSS2zQ4uH4kD8vTOJj6m"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval="minute1")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds','y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue




predict_price("KRW-XRP")
schedule.every().hour.do(lambda: predict_price("KRW-XRP"))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

cnt=0
# 자동매매 시작
while True:
    try:
        print('\ncnt :',cnt)
        cnt+=1

        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-XRP", 0.5)
            print('target price :', target_price)
            current_price = get_current_price("KRW-XRP")
            print('current price :', current_price)
            print('predicted_close_price : %.1f'%(predicted_close_price))
            if target_price < current_price and current_price < predicted_close_price:
                krw = get_balance("KRW")
                print('krw :', krw)
                if krw > 5000:
                    upbit.buy_market_order("KRW-XRP", krw*0.9995)
                    print('juno buy!!!!!!!!!!')
        else:
            XRP = get_balance("XRP")
            if XRP > 0.00008:
                upbit.sell_market_order("KRW-XRP", XRP*0.9995)
                print('juno sell!!!!!!!!!!')
        time.sleep(10)
    except Exception as e:
        print(e)
        time.sleep(1)

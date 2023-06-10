import pyupbit
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import datetime
import schedule
import time


# 액세스 키 설정
access_key = ""
secret_key = ""
upbit = pyupbit.Upbit(access_key, secret_key)
REPL = "KRW-XRP"


def get_historical_price(ticker, interval, count):
    try:
        df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
        if df is None:
            print("No data was returned from the API.")
            return None
        else:
            return df['close']
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


scaler = MinMaxScaler()

def preprocess_data(df):
    global scaler
    scaled_data = scaler.fit_transform(df.values.reshape(-1, 1))
    return scaled_data

# 시퀀스 생성
def create_sequences(data, seq_length):
    X = []
    y = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length])
    return np.array(X), np.array(y)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute", count=1)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0
def predict_price(ticker):
    global predicted_close_price

    # 비트코인 가격 데이터 받아오기
    btc_data = get_historical_price(ticker, "minute1", 500)
    btc_prices = preprocess_data(btc_data)

    # 학습 데이터와 테스트 데이터 분리
    train_size = int(len(btc_prices) * 0.8)
    train_data = btc_prices[:train_size]
    test_data = btc_prices[train_size:]

    # 시퀀스 생성
    seq_length = 10  # 입력 시퀀스 길이 설정
    X_train, y_train = create_sequences(train_data, seq_length)
    X_test, y_test = create_sequences(test_data, seq_length)

    # 모델 구성
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(128, return_sequences=True, input_shape=(seq_length, 1)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(64, return_sequences=True),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.LSTM(32),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    # 모델 컴파일
    model.compile(optimizer='adam', loss='mse')
    # 모델 학습
    model.fit(X_train, y_train, epochs=50, batch_size=32, shuffle=False)
    # 예측 수행
    y_pred = model.predict(X_test)
    # 스케일 역변환
    y_pred = scaler.inverse_transform(y_pred)
    y_test = scaler.inverse_transform(y_test)

    # 예측 결과 출력
    for i in range(len(y_pred)):
        print("실제 가격: {:.2f}, 예측 가격: {:.2f}".format(y_test[i][0], y_pred[i][0]))

    predicted_close_price = y_pred[-1][0]

    print('[juno] predicted_close_price : ', predicted_close_price)

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

maesu_price=0
maemae = 0

if __name__ == "__main__":
    predict_price(REPL)
    schedule.every(10).minutes.do(lambda: predict_price(REPL))

    cnt = 0
    while True:
        print('\ncnt :',cnt)
        cnt+=1

        now = datetime.datetime.now()
        start_time = get_start_time(REPL)
        end_time = start_time + datetime.timedelta(days=1)
        schedule.run_pending()

        target_price = get_target_price(REPL, 0.6) # k값 중요
        print('target price :', target_price)
        current_price = get_current_price(REPL)
        print('current price :', current_price)
        print('predicted_close_price : %.1f'%(predicted_close_price))
        if maemae == 0:
            if target_price < current_price < predicted_close_price:
                maesu_price = current_price

                krw = get_balance("KRW")

                print('krw :', krw)

                if krw > 5000:
                    upbit.buy_market_order(REPL, krw*0.9995)
                    print('juno buy!!!!!!!!!!')

            maemae = 1

        else : 
            if current_price > maesu_price*0.98:
                upbit.sell_market_order(REPL, REPL*0.9995)
                print('juno sell!!!!!!!!!!')

        time.sleep(60)



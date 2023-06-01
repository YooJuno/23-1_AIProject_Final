import pyupbit
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

# 액세스 키 설정
access_key = "VTJBxRRNXuS6lxzJsPGWlSC2xRvk8d7jGKAztoP1"
secret_key = "369wva72AmEcbLQjDOLQaSS2zQ4uH4kD8vTOJj6m"
upbit = pyupbit.Upbit(access_key, secret_key)

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

# 비트코인 가격 데이터 받아오기
btc_data = get_historical_price("KRW-XRP", "minute1", 500)
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
model.fit(X_train, y_train, epochs=20, batch_size=32, shuffle=False)

# 예측 수행
y_pred = model.predict(X_test)

# 스케일 역변환
y_pred = scaler.inverse_transform(y_pred)
y_test = scaler.inverse_transform(y_test)

# 예측 결과 출력
for i in range(len(y_pred)):
    print("실제 가격: {:.2f}, 예측 가격: {:.2f}".format(y_test[i][0], y_pred[i][0]))

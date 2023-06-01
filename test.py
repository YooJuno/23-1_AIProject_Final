import pyupbit
from fbprophet import Prophet

access = ""          # 본인 값으로 변경
secret = ""          # 본인 값으로 변경
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-XRP"))     # KRW-BTC 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회
# -*- coding: utf-8 -*-
import pprint
import pandas as pd
import sys
from time import sleep
import datetime
import os
import pyupbit
import traceback

access_key = "내 계정의 access_key 값"
secret_key = "내 계정의 secret_key 값"

upbit = pyupbit.Upbit(access_key, secret_key)


class trCoinBot:
    def __init__(self):
        print(pyupbit.Upbit)
        tickers = pyupbit.get_tickers() # 코인 이름 가져오기
        # print(tickers)

    def calTime(self):
        # 날짜 계산
        self.current = datetime.datetime.now()
        self.now_year = self.current.strftime("%Y")
        self.now_date = datetime.date.today().isoformat()

    def marketTimeCheck(self):
        # 현재 시간을 숫자로 계산한다. 
        self.current = datetime.datetime.now()
        self.now_time = (self.current.hour * 100) + self.current.minute


    def getAccBalance(self):
        # 계좌 잔고 조회
        r = upbit.get_balances()
        #print(r)

        r_balance = {}  
        # krw_balance : 보유중인 원화 잔고
        # avilable_krw : 매수 가능한 원화 잔고
        # coin_balance : 보유중인 코인 잔고
        # avg_buy_price : 보유중인 코인 매수 평단가
        # profit : 보유중인 코인 수익률

        fee = 0.05  # 거래 수수료
        # 자료형은 딕셔너리이다.
        try:
            # 현재 원화 잔고 얻어오기
            money =  float(r[0]['balance'])

            if r[0]['currency'] == 'KRW':
                print("현재 잔고는 원화로 %f 원 입나다." % money)

            r_balance['krw_balance'] = money

            # 매수 가능 금액 계산
            if money > 0: # 잔고가 있을때
                v = money * fee 
                r_balance['avilable_krw'] = money - v
                print("매수 가능 금액 : %f" % r_balance['avilable_krw'])
            else:
                r_balance['avilable_krw'] = 0
                print("매수 가능한 잔고가 없습니다.")

        except:
            print("계좌 잔고 값 얻어오기에서 에러가 발생했습니다.")
            r_balance['krw_balance'] = 0
            r_balance['coin_balance'] = 0
            r_balance['avg_buy_price'] = 0
            r_balance['avilable_krw'] = 0
            r_balance['profit'] = 0

            # 코인 보유량 얻어오기
        try:
            get_coin = float(r[1]['balance'])
            if get_coin > 0: 
                print("현재 보유중인 코인은 %0.15f 입니다." % get_coin)
                r_balance['coin_balance'] = get_coin
            else:
                print("코인이 없습니다.")
                r_balance['coin_balance'] = 0

            # 코인 평단가 얻어오기
            avg_buy_price = float(r[1]['avg_buy_price'])
            if avg_buy_price > 0:
                print("현재 보유중인 코인의 평균 단가는 %f 입니다" % avg_buy_price)
                r_balance['avg_buy_price'] = avg_buy_price
            else:
                r_balance['avg_buy_price'] = 0
            
            # 코인 수익률 계산
            if avg_buy_price > 0: # 잔고가 있을 경우
                now_price = self.getNowPrice("KRW-ETH")
                profit = ((now_price / avg_buy_price) - 1) * 100
                print("현재 보유중인 코인의 수익률은 %f 입니다. 현재가:%d, 보유가:%f" % (profit, now_price, avg_buy_price))
                r_balance['profit'] = profit
            else:
                r_balance['profit'] = 0

        except:
            print("코인 잔고가 없거나 얻어오기에서 에러가 발생했습니다.")
            r_balance['coin_balance'] = 0
            r_balance['avg_buy_price'] = 0
            r_balance['profit'] = 0

        return r_balance
        

    def buyOrderMarket(self, t, volume): # ticker, price
        print("시장가주문")
        # volume 는 매수 금액. 원화로 환산하여 주문한다.
        try:
            r = upbit.buy_market_order(t, volume)
            print(r)

        except:
            print("매수 주문이 실패하였습니다.")
  
    def sellOrderMarket(self, t, volume):
        print("시장가매도")
        # t는 코인의 종류(티커) 예를 들면 이더리움은 KRW-ETH, volume 은 보유 수량
        # volume에는 매도할 수량을 적는다. 최소 매도 수량은 원화로 5,000원 이상이어야 한다. 
        try:
            r = upbit.sell_market_order(t, volume)
            print(r)

        except:
            print("매도 주문이 실패하였습니다.")

    def getNowPrice(self, ticker):
        # 현재가 조회
        try:
            price = pyupbit.get_current_price([ticker])
            #print(price)

            return price
        except:
            print("현재가 조회시 오류가 발생하였습니다.")

            return 0
             

    def getOhlcv(self, t):
        # 일별 데이터 조회
        r = pyupbit.get_ohlcv(ticker=t)
        #print(type(r))

        return r.tail(2)

    def getOrderBook(self, t):
        # 호가 조회
        r = pyupbit.get_orderbook(ticker=t)
        print(r)


def main():
    c = trCoinBot()

    c.calTime()
    c.marketTimeCheck()
    c.getAccBalance()
    # c.buyOrderMarket()
    # c.sellOrderMarket()
    # c.getNowPrice()
if __name__ == "__main__":
    main()
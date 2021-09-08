# -*- coding: utf-8 -*-

import time
import spidev
import RPi.GPIO as GPIO

LEDPIN1 = 26
LEDPIN2 = 16
LEDPIN3 = 12
LEDPIN4 = 6
LEDPIN5 = 5

GPIO.setmode(GPIO.BCM)
# ピンの番号では無く、GPIOの番号を指定する
GPIO.setup(LEDPIN1, GPIO.OUT)
GPIO.setup(LEDPIN2, GPIO.OUT)
GPIO.setup(LEDPIN3, GPIO.OUT)
GPIO.setup(LEDPIN4, GPIO.OUT)
GPIO.setup(LEDPIN5, GPIO.OUT)

""" MCP3008からタイを取得するクラス """
class MCP3008_Class:
    
    """ コンストラクタ """
    def __init__(self, vcc, ch):
        self.vcc = vcc
        self.ch = ch
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz = 100000 # 必須の記述 (3.3V:100kHz, 5V:200kHz)
            
    """ 電圧取得 """
    def GetVoltage(self):
        
        # https://101010.fun/iot/raspi-spi.html#header-2
        # ↑ここのサイトの spi.xfer2([1, (8+ch)<<4, 0]) の解説がわかりやすかった
        adc = self.spi.xfer2([1, (8+self.ch)<<4, 0])
        
        # https://101010.fun/iot/raspi-spi.html#header-3
        # ↑ここのサイトの ((raw[1]&3) << 8) + raw[2] の解説がわかりやすかった
        data = ((adc[1]&3) << 8) + adc[2]
        volts = data * self.vcc / float(1023)
        volts = round(volts, 4) # 少数の丸め処理
        return volts
    
    """ 距離を推定する """
    def GetDist(self, volts):
        # 計算式参考（http://myct.jp/arduino/index.php?%E8%B7%9D%E9%9B%A2%E3%82%BB%E3%83%B3%E3%82%B5+GP2Y0A21YK0F）
        dist = 26.549 * pow(volts, -1.2091) 
        return dist
    
    """ 終了処理 """
    def Cleanup(self):
        self.spi.close()

"""
LED On Off
[距離 <= 10]のとき0つ点灯
[10 < 距離 <= 20]のとき1つ点灯
[20 < 距離 <= 30]のとき2つ点灯
[30 < 距離 <= 40]のとき3つ点灯
[40 < 距離 <= 50]のとき4つ点灯
[50 < 距離 <= 60]のとき5つ点灯
"""
def LedOnOff(dist):
    if dist <= 10:
        GPIO.output(LEDPIN1, GPIO.LOW)
        GPIO.output(LEDPIN2, GPIO.LOW)
        GPIO.output(LEDPIN3, GPIO.LOW)
        GPIO.output(LEDPIN4, GPIO.LOW)
        GPIO.output(LEDPIN5, GPIO.LOW)
    elif dist <= 20:
        GPIO.output(LEDPIN1, GPIO.HIGH)
        GPIO.output(LEDPIN2, GPIO.LOW)
        GPIO.output(LEDPIN3, GPIO.LOW)
        GPIO.output(LEDPIN4, GPIO.LOW)
        GPIO.output(LEDPIN5, GPIO.LOW)
    elif dist <= 30:
        GPIO.output(LEDPIN1, GPIO.HIGH)
        GPIO.output(LEDPIN2, GPIO.HIGH)
        GPIO.output(LEDPIN3, GPIO.LOW)
        GPIO.output(LEDPIN4, GPIO.LOW)
        GPIO.output(LEDPIN5, GPIO.LOW)
    elif dist <= 40:
        GPIO.output(LEDPIN1, GPIO.HIGH)
        GPIO.output(LEDPIN2, GPIO.HIGH)
        GPIO.output(LEDPIN3, GPIO.HIGH)
        GPIO.output(LEDPIN4, GPIO.LOW)
        GPIO.output(LEDPIN5, GPIO.LOW)
    elif dist <= 50:
        GPIO.output(LEDPIN1, GPIO.HIGH)
        GPIO.output(LEDPIN2, GPIO.HIGH)
        GPIO.output(LEDPIN3, GPIO.HIGH)
        GPIO.output(LEDPIN4, GPIO.HIGH)
        GPIO.output(LEDPIN5, GPIO.LOW)
    elif dist <= 60:
        GPIO.output(LEDPIN1, GPIO.HIGH)
        GPIO.output(LEDPIN2, GPIO.HIGH)
        GPIO.output(LEDPIN3, GPIO.HIGH)
        GPIO.output(LEDPIN4, GPIO.HIGH)
        GPIO.output(LEDPIN5, GPIO.HIGH)

""" main関数 """
if __name__ == '__main__':
    # chが0だとなぜか動かないので、1で実施する
    ADC = MCP3008_Class(vcc=3.3, ch=1)
    try:
        while True:
            volts = ADC.GetVoltage()
            dist = ADC.GetDist(volts=volts)
            LedOnOff(dist)
            
    except KeyboardInterrupt:
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        ADC.Cleanup()
        GPIO.cleanup()
        print("\nexit program")



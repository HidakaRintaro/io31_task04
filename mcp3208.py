#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import spidev

""" MCP3008からタイを取得するクラス """
class MCP3008_Class:
    
    """ コンストラクタ """
    def __init__(self, ref_volts, ch):
        self.ref_volts = ref_volts
        self.ch = ch
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)
        self.spi.max_speed_hz = 100000 # 3.3V:100kHz, 5V:200kHz
            
    """ 電圧取得 """
    def GetVoltage(self):
        
        # https://101010.fun/iot/raspi-spi.html#header-2
        # ↑ここのサイトの spi.xfer2([1, (8+ch)<<4, 0]) の解説がわかりやすかった
        adc = self.spi.xfer2([1, (8+self.ch)<<4, 0])
        
        # https://101010.fun/iot/raspi-spi.html#header-3
        # ↑ここのサイトの ((raw[1]&3) << 8) + raw[2] の解説がわかりやすかった
        data = ((adc[1]&3) << 8) + adc[2]
        volts = data / float(1023) * self.ref_volts 
        volts = round(volts, 4) # 少数の丸め処理
        return volts
    
    """ 距離を推定する """
    def GetDist(self):
        volts = self.GetVoltage()
        dist_inv = 0.0502 * volts - 0.0123 # 実測から求めた電圧と1/距離[cm]の近似直線
        dist = 1/dist_inv # 1/距離[1/cm]を距離[cm]に変換
        return dist
    
    """ 終了処理 """
    def Cleanup(self):
        self.spi.close()

""" main関数 """
if __name__ == '__main__':
    ADC = MCP3008_Class(ref_volts=3.3, ch=0)
    try:
        while True:
            volts = ADC.GetVoltage()
            dist = ADC.GetDist()
            print("volts: {:8.2f}".format(volts)) # 0.22 ~ 0.61
            print("{:8.2f} cm".format(dist))
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        ADC.Cleanup()
        print("\nexit program")



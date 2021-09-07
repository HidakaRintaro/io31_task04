# -*- coding: utf-8 -*-

import time
import spidev

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
        print("ad:{:.0f}".format(data))
        volts = data * self.vcc / float(1023)
        volts = round(volts, 4) # 少数の丸め処理
        return volts
    
    """ 距離を推定する """
    def GetDist(self, volts):
        dist = 26.549 * pow(volts, -1.2091) 
        return dist
    
    """ 終了処理 """
    def Cleanup(self):
        self.spi.close()

""" main関数 """
if __name__ == '__main__':
    ADC = MCP3008_Class(vcc=3.3, ch=0)
    try:
        while True:
            volts = ADC.GetVoltage()
            print("volts:{:1.2f}".format(volts))
            #dist = ADC.GetDist(volts=volts)
           # print("volts:  {:.2f},   {:.2f} cm".format(volts, dist)) 
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        ADC.Cleanup()
        print("\nexit program")



from __future__ import annotations
from hindsight.primitives import Candle
from enum import Enum
import talib as ta
import numpy as np

class CandleSource(Enum):
    Open  = 0
    High  = 1
    Low   = 2
    Close = 3
    Volume = 4

class DataExplorer:
    def __init__(self, candles: list[Candle]):
        self.candles : list[Candle] = candles
        self.ohlc : dict[CandleSource, np.ndarray] = {
            CandleSource.Open: np.fromiter((candle.open for candle in self.candles), dtype=np.float64),
            CandleSource.High: np.fromiter((candle.high for candle in self.candles), dtype=np.float64),
            CandleSource.Low: np.fromiter((candle.low for candle in self.candles), dtype=np.float64),
            CandleSource.Close: np.fromiter((candle.close for candle in self.candles), dtype=np.float64),
            CandleSource.Volume: np.fromiter((candle.volume for candle in self.candles), dtype=np.float64),
        }
        self.techs : dict = {}
        pass

    def has_tech(self,  type: str, props: dict) -> bool:
        if(type in self.techs.keys()):
            tech_data : list = self.techs[type]
            for tech in tech_data:
                if(tech["properties"] == props):
                    return True
        else:
            False  

    def ta_calculate(self, type: str, props: dict) -> np.ndarray:
        if(type == "SMA"):
            source : CandleSource = props["source"]
            return ta.SMA(self.ohlc[source], props["period"])
        elif(type == "EMA"):
            source : CandleSource = props["source"]
            return ta.EMA(self.ohlc[source], props["period"])
        elif(type == "ATR"):
            return ta.ATR(self.ohlc[CandleSource.High], self.ohlc[CandleSource.Low], self.ohlc[CandleSource.Close], props["period"])
        
        return np.ndarray([])

    def get_local_explorer(self, index: int) -> LocalDataExplorer:
        return LocalDataExplorer(self, index)

    def get_candle_at(self, index: int) -> Candle | None:
        if(index < 0 or index >= len(self.candles)):
            return None
        return self.candles[index]

    def get_candle_data(self, source: CandleSource) -> np.ndarray:
        return self.ohlc[source]

    def get_tech(self, index: int, type: str, props: dict) -> float:
        if(type in self.techs.keys()):
            tech_data : list = self.techs[type]
            for tech in tech_data:
                if(tech["properties"] == props):
                    return tech["value"][index]                    
        else:
            self.techs[type] = []

        data = self.ta_calculate(type, props)
        self.techs[type].append({
            "properties": props,
            "value": data
        })
        return data[index]

    def get_tech_full(self, type: str, props: dict) -> np.ndarray:
        if(type in self.techs.keys()):
            tech_data : list = self.techs[type]
            for tech in tech_data:
                if(tech["properties"] == props):
                    return tech["value"]                  
        else:
            self.techs[type] = []

        data = self.ta_calculate(type, props)
        self.techs[type].append({
            "properties": props,
            "value": data
        })
        return data
    

    def get_tech_sma(self, period: int, source : CandleSource = CandleSource.Close) -> np.ndarray:
        return self.get_tech_full("SMA", {
            "period": period,
            "source" : source
        })
    def get_tech_ema(self, period: int, source : CandleSource = CandleSource.Close) -> np.ndarray:
        return self.get_tech_full("EMA", {
            "period": period,
            "source" : source
        })
    def get_tech_atr(self, period: int) -> np.ndarray:
        return self.get_tech_full("ATR", {
            "period": period
        })

class LocalDataExplorer:
    def __init__(self, parent : DataExplorer, index: int):
        self.parent : DataExplorer = parent
        self.index : int = index

    def get_current_candle(self) -> Candle | None:
        return self.parent.get_candle_at(self.index)

    def get_tech_sma(self, period: int, source : CandleSource = CandleSource.Close) -> float:
        return self.parent.get_tech(self.index, "SMA", {
            "period": period,
            "source" : source
        })
    def get_tech_ema(self, period: int, source : CandleSource = CandleSource.Close) -> float:
        return self.parent.get_tech(self.index, "EMA", {
            "period": period,
            "source" : source
        })
    def get_tech_atr(self, period: int) -> float:
        return self.parent.get_tech(self.index, "ATR", {
            "period": period
        })
from abc import ABC, abstractmethod
from hindsight.data_explorer import DataExplorer, LocalDataExplorer
import numpy as np

class Filter(ABC):
    @abstractmethod
    def prepare(self, explorer: DataExplorer) -> None:
        ...
    @abstractmethod
    def run(self, explorer: LocalDataExplorer) -> bool:
        ...


class FilterPipeline:
    def __init__(self, filters: list[Filter]):
        self.filters : list[Filter]= filters
        self.candle_mask : np.ndarray[bool] = []

    def run(self, explorer: DataExplorer) -> None:
        candle_count = len(explorer.candles)
        self.candle_mask : np.ndarray = np.ones(candle_count, dtype=bool)

        for filter in self.filters:
            filter.prepare(explorer)
            for ci in range(candle_count):
                if(self.candle_mask[ci]):
                    self.candle_mask[ci] = filter.run(explorer.get_local_explorer(ci))

        
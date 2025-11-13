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
        total_candles = len(explorer.candles)
        self.candle_mask : np.ndarray = np.ones(total_candles, dtype=bool)

        print(f"Processing {len(explorer.candles)} candles")
        print("-" * 20)

        for filter in self.filters:
            filter.prepare(explorer)
            discard_count = 0
            passed_count = 0
            for ci in range(total_candles):
                if(self.candle_mask[ci]):
                    self.candle_mask[ci] = filter.run(explorer.get_local_explorer(ci))
                    if(self.candle_mask[ci]):
                        passed_count += 1
                    else:
                        discard_count += 1

            # Print out how many candles the filter passed out of all candles
            filter_name = filter.__class__.__name__
            print(f"Filter: {filter_name}")
            print(f"Candles Discarded: {discard_count}")
            print(f"Candles Passed: {passed_count}")
            print("-" * 20)

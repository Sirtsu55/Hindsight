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

    @abstractmethod
    def passthrough(self) -> np.ndarray | None:
        ...


class FilterPipeline:
    def __init__(self, filters: list[Filter]):
        self.filters : list[Filter]= filters

    def run(self, explorer: DataExplorer) -> np.ndarray:
        total_candles = len(explorer.candles)
        candle_mask : np.ndarray[bool] = np.ones(total_candles, dtype=bool)

        print(f"Processing {len(explorer.candles)} candles")
        print("-" * 20)

        for filter in self.filters:
            filter.prepare(explorer)
            discard_count = 0
            passed_count = 0
            for ci in range(total_candles):
                if(candle_mask[ci]):
                    passed = filter.run(explorer.get_local_explorer(ci))
                    if(passed):
                        passed_count += 1
                    else:
                        discard_count += 1
                    candle_mask[ci] = passed

            force_passes = filter.passthrough()
            if(force_passes is not None):
                candle_mask[force_passes] = True

            # Print out how many candles the filter passed out of all candles
            filter_name = filter.__class__.__name__
            print(f"Filter: {filter_name}")
            print(f"Candles Discarded: {discard_count}")
            print(f"Candles Passed: {passed_count}")
            print("-" * 20)

        return candle_mask 
    
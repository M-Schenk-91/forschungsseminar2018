
from enum import Enum


class Filter:

    # usage: Filter.Filter.MovingAverage()
    class MovingAverage:

        # usage: Filter.Filter.MovingAverage.MovingAverageTypes.TYPE.value
        class MovingAverageTypes(Enum):
            NORMAL = 1
            ADAPTIVE = 2
            WEIGHTED = 3
            SUM_MODES = 3

        @staticmethod
        def apply(data, mode=MovingAverageTypes.NORMAL.value):
            if mode == Filter.MovingAverage.MovingAverageTypes.NORMAL.value:
                return sum(data) / len(data)

            raise NotImplementedError("Adaptive and Weighted are not implemented yet")

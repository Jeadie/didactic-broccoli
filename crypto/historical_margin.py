# Scripts for checking, via Shrimpy, potential single pair arbitrages (simple 
# buy sell on separate exchanges) for a variety of pairs and excahnges. Uses
#  historical data to calculate average difference between the two exchanges,
#  weighted by the duration of the difference. Historical trades are used as 
# market value at given time. 
import datetime
import logging
import json
import os
import sys
from typing import Dict, List

#mimick datetime class function in Python3.7
datetime.fromisoformat = lambda x: datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ")

from util import make_client, set_credential_from_file,timedelta_to_float


_logger = logging.getLogger()
logging.getLogger().setLevel(logging.DEBUG)

    
def margin(a:float,b:float ) -> float:
    """ Gets the percentage margin between the two values. """
    return 200.0* (a-b) / (a+b)

class HistoricalTradeAnalysis(object):

    def __init__(self, e1, e2):
        """
        Args:
            e1: Trade history of a pair on exchange 1.
            e2: Trade history of a pair on exchange 2.

        """
        self.e1 = e1
        self.e2 = e2

    def get_historic_margin(self) -> float:
        """

        """
        differences = self.get_trade_margin()
        return sum([abs(x) for x in differences])/len(differences)

    def get_trade_margin(self) -> List[float]:
        """

        Returns:
            A list of percentage differences between the two exchanges at each 
            timepoint when a trade happens on one of the exchanges.
        """
        margins = []
        if len(self.e1) > 0:
            t1 = self.e1.pop(0)  
        if len(self.e2) > 0:
            t2 = self.e2.pop(0)
        while len(self.e1) > 0 or len(self.e2) > 0:
            margins.append(self.compute_margin_value(t1, t2))
            
            d1 = datetime.fromisoformat(t1["time"])
            d2 = datetime.fromisoformat(t2["time"])

            if d1 <= d2 and len(self.e1) > 0:
                t1 = self.e1.pop(0)  
            if d2 < d1 and len(self.e2) > 0:
                t2 = self.e2.pop(0)
            else:
                return self.post_trade_margin_func(margins, t1, t2)
        return self.post_trade_margin_func(margins, t1, t2)

    def post_trade_margin_func(self, margins: List[float], t1: Dict[str, str], t2: Dict[str, str]) -> List[float]:
        return margins

    def compute_margin_value(self, t1: Dict[str, str], t2: Dict[str, str]) -> float:
        return margin(
                    float(t1['price']),
                    float(t2['price'])
                )

class WeightedHistoricalTradeAnalysis(HistoricalTradeAnalysis):
    def __init__(self, e1, e2):
        super().__init__(e1, e2)
        self.entire_starttime = datetime.fromisoformat(min(self.e1[0]['time'], self.e2[0]['time']))

    def post_trade_margin_func(self, margins: List[float], t1: Dict[str, str], t2: Dict[str, str]) -> List[float]:
        end_time = datetime.fromisoformat(max(t1['time'], t2['time']))
        return [ m /(timedelta_to_float(end_time - self.entire_starttime)) for m in margins]

    def get_duration_of_margin(self, t1: Dict[str, str], t2: Dict[str, str]) -> datetime.timedelta:
        start_time = datetime.fromisoformat(min(t1['time'], t2['time']))
        end_time = None
        #Use convoluted except handling to efficiently handle unlikely IndexError exceptions. 

        try:
            end_datetime1 = self.e1[0]['time']
        except IndexError:
            try:
                # Handle e1 empty    entire_starttime
                end_datetime2 = self.e2[0]['time']
                end_time = datetime.fromisoformat(max(t1['time'], end_datetime2))

            except IndexError:
                # Handle e1, e2 empty. Use larger of two times (result ends up being difference in times between t1, t2).    
                end_time = datetime.fromisoformat(max(t1['time'], t2['time']))

        if not end_time:
            # No exception from above, process end_datetime2
            try: 
                # Handles unempty t1, unempty t2
                end_datetime2 = self.e2[0]['time']
                end_time = datetime.fromisoformat(min(end_datetime1, end_datetime2))

            except IndexError:
                #handle empty t2, unempty t1
                end_time = datetime.fromisoformat(max(end_datetime1, t2['time']))

        return end_time - start_time

    def compute_margin_value(self, t1: Dict[str, str], t2: Dict[str, str]) -> float:
        return margin(
                    float(t1['price']),
                    float(t2['price'])
         ) * timedelta_to_float(self.get_duration_of_margin(t1, t2))


def main(argv, argc) -> int:
    if argc < 1:
        _logger.error(
            f"Did not specify a Shrimpy credentials file."
        )
        return 1
    if not set_credential_from_file(argv[1]):
        _logger.error(
            f"UNable to set Shrimpy API credentials from file. No credential file specified."
        )
        return 1

    start_date = datetime.datetime(2021, 1, 1)
    end_date = datetime.datetime(2021, 2, 1)
    limit = 200
    coin = "DOGE"
    base="USDT"
    _id = f"{coin}_{limit}_{start_date.strftime('%d%m%Y')}_{end_date.strftime('%d%m%Y')}"

    if not os.path.exists(f"{_id}.json"):
        data = {}
        c = make_client()
        exchanges = c.get_supported_exchanges()
        for v in exchanges:
            history = c.get_historical_trades(
                v['exchange'],
                coin,
                base,
                start_date.isoformat(),
                end_date.isoformat(),
                limit
            )
            if type(history) == list:
                v["history"] = history
                data[v['exchange']] = v

        with open(f"{_id}.json", 'w') as f:
            json.dump(data, f)
    

    with open(f"{_id}.json", 'r') as f:
        data = json.load(f)

    exchanges = list(data.keys())
    for e in exchanges:
        if type(data[e]["history"]) == dict:
            data.pop(e)
    exchanges = list(data.keys())


    results = []
    results.append(
        "exchange1,exchange2,transactions,margin,marginslessfees\n"
    )
    for i in range(len(exchanges)):
        for j in range(i+1, len(exchanges)):
            e1 = exchanges[i]
            e2 = exchanges[j]
            margin = HistoricalTradeAnalysis(data[e1]["history"], data[e2]["history"]).get_historic_margin()
            print(
                f"{e1} - {e2}: transactions: {min(len(data[e1]['history']), len(data[e2]['history']))}. margin: {margin}. Margin less fees: {margin  - data[e1]['worstCaseFee'] - data[e2]['worstCaseFee']}."
            )
            results.append(
                f"{e1},{e2},{min(len(data[e1]['history']), len(data[e2]['history']))},{margin},{margin  - data[e1]['worstCaseFee'] - data[e2]['worstCaseFee']}\n"
            )

    with open(f"{_id}.csv", "w") as f:
        f.writelines(results)

    return 0

if __name__ == '__main__':
    main(sys.argv, len(sys.argv))

    
from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import json
import pandas as pd

candlestick = int

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: Dict[Symbol, List[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()

class Trader:

    def run(self, state: TradingState) -> Dict[Symbol, List[Order]]:
        """
        Trading algorithm that uses order book depth, market trends, and volatility to make trading decisions
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: List[Order] = []

                for bid in order_depth.buy_orders.keys():
                    if bid >= 10000:
                        orders.append(Order(product, bid, order_depth.buy_orders[bid]))

                for ask in order_depth.sell_orders.keys():
                    if ask <= 10000:
                        orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                result[product] = orders


            elif product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                bids = order_depth.buy_orders.keys()
                asks = order_depth.sell_orders.keys()

                price = (min(bids) + max(asks))/2

                print(state.timestamp)

                if state.timestamp == 0:
                    first = {'price': price, 'candlestick': 1, 'candlestick_max': price, 'candlestick_min': price}
                    hist_prices = pd.DataFrame(first)
                
                else:
                    candlestick = int (state.timestamp/30)+1
                    candlestick_max = hist_prices[hist_prices['candlestick'] == candlestick].max()
                    candlestick_min = hist_prices[hist_prices['candlestick'] == candlestick].min()
                    candlestick_max, candlestick_min = price

                    hist_prices.loc[len(hist_prices)] = [price, candlestick, candlestick_max, candlestick_min]

                hist_prices.loc[hist_prices['candlestick'] == candlestick, 'candlestick_max'] = candlestick_max
                hist_prices.loc[hist_prices['candlestick'] == candlestick, 'candlestick_min'] = candlestick_min

                avgmax_last_20_sticks = hist_prices.iloc['candlestick_max', -600:].mean()
                avgmin_last_20_sticks = hist_prices.iloc['candlestick_min', -600:].mean()

                #if price passes above avgmax_last_20_sticks, buy all
                #if price drops below avgmin_last_20_sticks, sell all
                #if price passes above avgmax_last_20_sticks + [(avgmax-avgmin)*1.5], sell all


        logger.flush(state, result)
        return result

    # Return the method output dict
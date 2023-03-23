from typing import Dict, List, Any
from datamodel import OrderDepth, TradingState, Order, ProsperityEncoder, Symbol
import json
import pandas as pd

hist_prices = pd.DataFrame(columns=['price', 'candlestick', 'candlestick_max', 'price_at_buy'])

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
                
                candlestick = (state.timestamp/30)+1
                candlestick_df = hist_prices[hist_prices['candlestick'] == candlestick]
                candlestick_max = candlestick_df['price'].max()

                hist_prices.loc[len(hist_prices)] = [price, candlestick, candlestick_max, price]

                hist_prices.loc[hist_prices['candlestick'] == candlestick, 'candlestick_max'] = candlestick_max

                avgmax_last_20_sticks = hist_prices.loc[-600:, 'candlestick_max'].mean()

                last_price = hist_prices.iloc[-1].loc['price']

                if price > avgmax_last_20_sticks and last_price <= avgmax_last_20_sticks:
                    for bid in bids:
                        orders.append(Order(product, bid, order_depth.buy_orders[bid]))
                    
                    hist_prices.at[0, 'price_at_buy'] = price

                elif price < hist_prices.at[0, 'price_at_buy']*0.99 and last_price >= hist_prices.at[0, 'price_at_buy']*0.99:
                    for ask in asks:
                        orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

                elif price > hist_prices.at[0, 'price_at_buy']*1.02 and last_price <= hist_prices.at[0, 'price_at_buy']*1.02:
                    for ask in asks:
                        orders.append(Order(product, ask, -order_depth.sell_orders[ask]))


        logger.flush(state, result)
        return result

    # Return the method output dict
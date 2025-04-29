# utils/calculate_median.py

def calculate_median(prices):
    prices.sort()
    n = len(prices)
    mid = n // 2

    if n % 2 == 0:
        return (prices[mid - 1] + prices[mid]) / 2
    else:
        return prices[mid]

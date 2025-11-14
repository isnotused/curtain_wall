import math

def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制值在[min, max]范围内"""
    return max(min_val, min(max_val, value))

def max_val(array: list) -> float:
    """计算列表最大值"""
    return max(array) if array else 0

def min_val(array: list) -> float:
    """计算列表最小值"""
    return min(array) if array else 0

def standard_deviation(array: list) -> float:
    """计算列表标准差"""
    if not array or len(array) == 1:
        return 0.0
    avg = sum(array) / len(array)
    variance = sum((x - avg) **2 for x in array) / len(array)
    return math.sqrt(variance)

def normalize(value: float, min_val: float, max_val: float) -> float:
    """归一化值至[0,1]"""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)
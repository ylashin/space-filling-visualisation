import random
import math
from typing import List
from functools import lru_cache
from hilbertcurve.hilbertcurve import HilbertCurve
from classes import Point
import pandas as pd

@lru_cache
def get_hilbert_points_map(dimension_size: int):
    p = dimension_size
    n=2
    hilbert_curve = HilbertCurve(p, n)
    distances = list(range(2**p))
    points = hilbert_curve.points_from_distances(distances)
    zipped = zip(points, distances)
    return {(p[0], p[1]):distance for p, distance in zipped}


def get_hilbert_order(dimension_size, x, y):
    map = get_hilbert_points_map(dimension_size)    
    return map[(x,y)]

def get_zorder(dimension_size, x, y):
    bit_size = int(math.log2(dimension_size))
    # 30 below is just an arbitrary big size of bits
    xb = f"{x:>030b}"[(30 - bit_size):]
    yb = f"{y:>030b}"[(30 - bit_size):]

    interleaved = ""
    for i in range(bit_size):
        interleaved += f"{yb[i]}{xb[i]}"
    zorder = int(interleaved, 2)
    return zorder



def get_linear_order(placement_method, dimension_size, x, y):
    if placement_method == "Random":
        return None
    if placement_method == "ZOrder":
        return get_zorder(dimension_size,x, y)
    if placement_method == "Hilbert":
        return get_hilbert_order(dimension_size,x, y)


def get_file_placement(placement_method, linear_order, file_count, dimension_size):
    if placement_method == "Random":
        return int(random.choice(list(range(int(file_count)))))
    if placement_method == "ZOrder" or placement_method == "Hilbert":
        records_per_file = (dimension_size * dimension_size / file_count)
        file_placement = linear_order // records_per_file
        return int(file_placement)

def get_points_connection_lines(points: List[Point]):
    lines_df = pd.DataFrame({
            "x": [p.x for p in points],
            "y": [p.y for p in points],
            "linear_order": [p.linear_order for p in points]
        })
    
    return lines_df

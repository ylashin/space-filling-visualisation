from typing import List
from dataclasses import dataclass
import pandas as pd

@dataclass
class Point:
    x: int
    y: int
    linear_order: int = None


class DataFile:
    def __init__(self, name) -> None:
        self.points = []
        self.name = name

    def add_point(self, p: Point) -> None:
        self.points.append(p)

    @property
    def dataframe(self) -> pd.DataFrame:
        x = [p.x for p in self.points]
        y = [p.y for p in self.points]
        names = [self.name for _ in range(len(self.points))]
        linear_orders = [x.linear_order for x in self.points]
        
        return pd.DataFrame({"x": x, "y":y, "file": names, "linear_order": linear_orders})
    
    @property
    def sorted_points(self) -> List[Point]:
        sorted_list = sorted(self.points, key=lambda x: x.linear_order) 
        return sorted_list


    @property
    def last_point(self) -> Point:
        return self.sorted_points[len(self.points) - 1]

    @property
    def first_point(self) -> Point:
        return self.sorted_points[0]

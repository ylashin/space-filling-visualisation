import math
from typing import List
import streamlit as st
import altair as alt
import pandas as pd
import itertools
from hilbertcurve.hilbertcurve import HilbertCurve
import random
from functools import lru_cache
from dataclasses import dataclass

st.set_page_config(page_title="Space Filling Techniques", layout="wide")

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


number_of_records = st.selectbox("Number of records", [2**4, 2**6, 2**8, 2**10], index=2)
number_of_files = st.text_input(label="File Count", value="8")
placement_method = st.selectbox("Placement method", ["Random", "ZOrder", "Hilbert"])

if placement_method:
    dimension_size = int(math.sqrt(int(number_of_records)))
    cross_product = list(itertools.product(range(int(dimension_size)), range(int(dimension_size))))
    points = [Point(x=c[0], y=c[1]) for c in cross_product]
    files = [DataFile(f"file_{f:04}") for f in range(int(number_of_files))]

    for p in points:
        p.linear_order = get_linear_order(placement_method, dimension_size, p.x, p.y)
        file_for_point = get_file_placement(placement_method, p.linear_order, int(number_of_files), dimension_size)
        #
        files[file_for_point].add_point(p)

    
    data_frames = [f.dataframe for f in files]
    records = pd.concat(data_frames)

    scatter_plot = alt.Chart(records, height=600, width=600).mark_circle(size=100).encode(
        x="x:Q",
        y="y:Q",
        color="file",
        tooltip=["x", "y", "file", "linear_order"]
    ).properties(
        title=f"Mapping records to files using {placement_method} strategy"
    )

    if placement_method in ["ZOrder", "Hilbert"]:
        lines_df = get_points_connection_lines(points)
        line_chart = alt.Chart(lines_df).mark_line(color="gray", width=2).encode(
            x="x",
            y="y",
            order="linear_order"
        )

        composit_plot = scatter_plot + line_chart
        st.altair_chart(composit_plot)
    else:
        st.altair_chart(scatter_plot)


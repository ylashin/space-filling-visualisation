import math
from typing import List
import streamlit as st
import altair as alt
import pandas as pd
import itertools
from classes import Point, DataFile
from helpers import get_linear_order, get_file_placement, get_points_connection_lines

st.set_page_config(page_title="Space Filling Techniques", layout="centered")


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


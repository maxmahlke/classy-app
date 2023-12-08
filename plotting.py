import itertools

from bokeh.models import Legend
from bokeh.plotting import figure
import classy
import streamlit as st


def plot_spectra(which):
    spectra = (
        st.session_state.SPECTRA_USER.values()
        if which == "user"
        else st.session_state.SPECTRA_LIT
    )
    p = figure(
        x_axis_label="Wavelength / μm",
        y_axis_label="Reflectance",
        toolbar_location="below",
        height=400,
    )

    colors = classy.plotting.get_colors(
        len(spectra) if len(spectra) != 3 else len(spectra) + 1, cmap="Spectral"
    )
    dashes = itertools.cycle(["solid", "dashed", "dotted", "dotdash", "dashdot"])

    legend_items = []

    for spec in spectra:
        line = p.line(
            spec.wave,
            spec.refl,
            line_width=2,
            line_color=colors.pop(),
            line_dash=next(dashes),
        )
        legend_items.append((spec.name if which != "user" else spec.filename, [line]))
    p.add_layout(Legend(items=legend_items, location=(10, 210)))
    st.bokeh_chart(p, use_container_width=True)

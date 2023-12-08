import itertools

from bokeh.plotting import figure
import pandas as pd
import streamlit as st
import classy


def parse_uploaded_files():
    """"""

    idx_invalid = _check_validity()
    _parse_spectra(idx_invalid)


def _parse_spectra(idx_invalid):
    """Create classy.Spectrum instances from uploaded user spectra."""

    # Removing invalid files is not possible, so we just skip them
    for i, file in enumerate(st.session_state.uploaded_spectra):
        if i in idx_invalid:
            continue

        data = pd.read_csv(file)

        st.session_state.SPECTRA_USER[file.name] = classy.Spectrum(
            wave=data.wave,
            refl=data.refl,
            refl_err=data.refl_err if "refl_err" in data.columns else None,
            filename=file.name,
        )


def _check_validity():
    """Ensure that uploaded spectra are valid CSV files with wave and refl columns."""

    idx_invalid = []

    for idx, file in enumerate(st.session_state.uploaded_spectra):
        # Check files
        try:
            data = pd.read_csv(file)
        except pd.errors.ParserError:
            st.warning(f"Uploaded file '{file.name}' is not a CSV file.", icon="⚠️")
            idx_invalid.append(idx)
            continue

        if not all(col in data.columns for col in ["wave", "refl"]):
            st.warning(
                f"Uploaded CSV file '{file.name}' does not contain 'wave' or 'refl' columns.",
                icon="⚠️",
            )
            idx_invalid.append(idx)
    return idx_invalid


def plot_spectra():
    p = figure(
        x_axis_label="Wavelength / μm",
        y_axis_label="Reflectance",
        toolbar_location="below",
        height=400,
    )

    colors = classy.plotting.get_colors(
        len(st.session_state.SPECTRA_USER), cmap="Spectral"
    )
    dashes = itertools.cycle(["solid", "dashed", "dotted", "dotdash", "dashdot"])

    for spec in st.session_state.SPECTRA_USER.values():
        p.line(
            spec.wave,
            spec.refl,
            legend_label=spec.filename,
            line_width=2,
            line_color=colors.pop(),
            line_dash=next(dashes),
        )

    # TODO: Upload example file
    # TODO: Possibility to enter target for each uploaded file
    # TODO: Plot spectra as uploaded

    st.bokeh_chart(p, use_container_width=True)

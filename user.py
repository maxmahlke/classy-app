import classy
import pandas as pd
import rocks
import streamlit as st

import plotting
import text


def layout():
    st.markdown("---")
    st.markdown("**Optional: Upload Your Spectra**")

    left, right = st.columns(2)
    with left:
        with st.expander(
            "Upload CSV files"
            if not st.session_state.SPECTRA_USER
            else f"{len(st.session_state.SPECTRA_USER)}"
        ):
            files = st.file_uploader(
                "Select one or more spectra to upload.",
                accept_multiple_files=True,
                help=text.HELP_DATA_UPLOAD,
                key="uploaded_spectra",
            )

            if files:
                _parse_spectra()

        if st.session_state.SPECTRA_USER:
            with st.expander("Optional: Define Targets"):
                targets = {}
                for file in files:
                    col1, col2 = st.columns(2)

                    with col1:
                        targets[file.name] = st.text_input(
                            label=f"Define target of `{file.name}`",
                            key=file.name,
                            help=text.TARGETS,
                        )

                    if targets[file.name]:
                        name, number = rocks.id(targets[file.name])

                        if name is not None:
                            st.session_state.SPECTRA_USER[file.name].set_target(name)

                    with col2:
                        if targets[file.name] and name is not None:
                            st.markdown("")
                            st.markdown("")
                            st.markdown(
                                f":white_check_mark: Resolved as: `({number}) {name}`"
                            )
                        else:
                            st.markdown("")
                            st.markdown("")
                            st.markdown(":warning: Unresolved")

            # with st.expander("Optional: Preprocess"):
            #     st.markdown("To be implemented.")

    with right:
        if st.session_state.SPECTRA_USER:
            plotting.plot_spectra("user")


def _parse_spectra():
    """Create classy.Spectrum instances from uploaded user spectra."""

    # Removing invalid files is not possible, so we just skip them
    for file in st.session_state.uploaded_spectra:
        try:
            data = pd.read_csv(file)
        except (pd.errors.ParserError, pd.errors.EmptyDataError):
            st.error(f":x: Uploaded file `{file.name}` is not a CSV file or empty.")
            continue

        if not all(col in data.columns for col in ["wave", "refl"]):
            st.error(
                f":x: Uploaded CSV file '{file.name}' does not contain 'wave' or 'refl' columns."
            )
            continue

        st.session_state.SPECTRA_USER[file.name] = classy.Spectrum(
            wave=data.wave,
            refl=data.refl,
            refl_err=data.refl_err if "refl_err" in data.columns else None,
            filename=file.name,
        )

    update_session_spectra()


def update_session_spectra():
    if not st.session_state.SPECTRA_LIT:
        spectra = classy.Spectra(list(st.session_state.SPECTRA_USER.values()))
    if not st.session_state.SPECTRA_USER:
        spectra = st.session_state.SPECTRA_LIT
    if st.session_state.SPECTRA_USER and st.session_state.SPECTRA_LIT:
        spectra = st.session_state.SPECTRA_LIT + list(
            st.session_state.SPECTRA_USER.values()
        )

    colors = classy.plotting.get_colors(len(spectra), cmap="jet")
    for i, spec in enumerate(spectra):
        spec._color = colors[i]
    st.session_state.SPECTRA = spectra

import itertools
import os

from bokeh.models import Legend
from bokeh.plotting import figure
import pandas as pd
import rocks
import streamlit as st

st.set_page_config(layout="wide")

os.environ["CLASSY_DATA_DIR"] = "./data/"
os.environ["ROCKS_CACHE_DIR"] = "no-cache"
rocks.config.CACHELESS = True
import classy  # noqa

classy.config.APP_MODE = True

spectra = []
spectra_lit = []
spectra_user = {}
st.image(
    "https://raw.githubusercontent.com/maxmahlke/classy/master/docs/_static/logo_classy.svg"
)

left, right = st.columns(2)

with left:
    st.markdown(
        "Welcome to the web interface of `classy`, a tool for the analysis of asteroid reflectance spectra. "
        "This interface provides basic functionality. For the full feature set, you can have a look at the `python` package "
        "[here](https://classy.readthedocs.io)."
    )

with right:
    st.markdown(
        "This interface allows to visualise, classify, and export reflectance spectra and their metadata. You can provide your "
        "own data, use literature data, or a combination of the two. To get started, just keep scrolling."
    )

st.markdown("---")

st.header("Your data")
left, right = st.columns(2)
with left:
    HELP_UPLOAD = """
    Upload one or more plain text files that contain one spectrum each.
    The file should be comma-separated and have at least two columns: `wave` and `refl`.
    Each row corresponds to one bin of the spectrum.

    Example File:


        wave,refl,refl_err
        0.374,0.915,0.0007
        0.418,0.941,0.0005
        0.462,0.966,0.0004
        0.506,0.997,0.0005
        0.55,1.0,0.0005
        0.594,1.010,0.0005
        0.638,1.001,0.0005
        0.682,1.013,0.0005
        0.726,1.025,0.0005
        0.77,1.033,0.0005
        0.814,1.037,0.0005
        0.858,1.033,0.0005
        0.902,1.021,0.0006
        0.946,1.034,0.0006
        0.99,1.067,0.00067
        1.034,1.114,0.0007

    """
    # TODO: Upload example file
    with st.expander("Upload"):
        uploaded_files = st.file_uploader(
            "Select one or more spectra to upload.",
            type=None,
            accept_multiple_files=True,
            key=None,
            help=HELP_UPLOAD,
            on_change=None,
            args=None,
            kwargs=None,
            disabled=False,
            label_visibility="visible",
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                data = pd.read_csv(uploaded_file)

                spectra_user[uploaded_file.name] = classy.Spectrum(
                    wave=data.wave,
                    refl=data.refl,
                    refl_err=data.refl_err if "refl_err" in data.columns else None,
                )

                # TODO: Cache a bft table, remove some odd columns
                # tar gz format
                # Merge bft with index, make rocks queries unnecessary, we only want the albedo anyways
                #
                # index in parquet format?
                #
                # TODO: Make size of index more apparent, give more examples
                # "65k spectra, most common sources: SMASS, Gaia, most common shortbib: ..."
                # "most common asteroid: ..."
                # Make full width,

    if uploaded_files:
        with st.expander("Optional: Define Targets"):
            st.markdown(
                "For each spectrum, define the asteroidal target by providing an identifier. "
                "The benefits of doing so are described [here](https://classy.readthedocs.io/en/latest/core.html#assigning-a-target)."
            )
            targets = {}
            for uploaded_file in uploaded_files:
                col1, col2 = st.columns(2)

                with col1:
                    targets[uploaded_file.name] = st.text_input(
                        label=f"Define asteroidal target of `{uploaded_file.name}`",
                        key=uploaded_file.name,
                        label_visibility="visible",
                        placeholder=uploaded_file.name,
                    )

                if targets[uploaded_file.name]:
                    name, number = rocks.id(targets[uploaded_file.name])

                    if name is not None:
                        spectra_user[uploaded_file.name].set_target(name)

                with col2:
                    # st.markdown(f"`{uploaded_file.name}`")

                    if targets[uploaded_file.name] and name is not None:
                        st.markdown("")
                        st.markdown("")
                        st.markdown(
                            f":white_check_mark: Resolved as: `({number}) {name}`"
                        )
                    else:
                        st.markdown("")
                        st.markdown("")
                        st.markdown(":x: Unresolved")

            # TODO: Upload example file
            # TODO: Possibility to enter target for each uploaded file
            #
        with st.expander("Optional: Preprocess"):
            st.markdown("To be implemented.")

with right:
    if uploaded_files:
        if uploaded_files:
            p = figure(
                x_axis_label="Wavelength / μm",
                y_axis_label="Reflectance",
                toolbar_location="below",
                height=400,
            )

            colors = classy.plotting.get_colors(len(uploaded_files), cmap="Spectral")
            dashes = itertools.cycle(
                ["solid", "dashed", "dotted", "dotdash", "dashdot"]
            )

            for uploaded_file in uploaded_files:
                spec = spectra_user[uploaded_file.name]

                p.line(
                    spec.wave,
                    spec.refl,
                    legend_label=uploaded_file.name,
                    line_width=2,
                    line_color=colors.pop(),
                    line_dash=next(dashes),
                )

            # TODO: Upload example file
            # TODO: Possibility to enter target for each uploaded file
            # TODO: Plot spectra as uploaded

            st.bokeh_chart(p, use_container_width=True)

st.markdown("---")
st.header("Literature data")
left, right = st.columns(2)

with left:
    st.markdown(
        "Here you can select spectra from the literature to include in your analysis. Write a query and select the spectra you are interested by marking it in the `select` column."
    )

    def parse_input(args):
        """Separate identifiers and option key-value pairs from arguments."""

        # Separate query parameters and identifiers
        args = args.split()
        idx_options = [i for i, arg in enumerate(args) if arg.startswith("--")]
        kwargs = (
            {args[i].strip("--"): args[i + 1] for i in idx_options}
            if idx_options
            else {}
        )

        id = args[: min(idx_options)] if idx_options else args
        id = None if not id else id
        return id, kwargs

    HELP_INPUT = """
    Enter a query for spectra in the ``classy`` spectra database.
    The query language is explained [here](https://classy.readthedocs.io/en/latest/select.html).

    Example queries:

    ``ceres`` - All spectra of (1) Ceres

    ``4 --wave_min 0.45 --wave_max 2.45`` - VisNIR spectra of (4) Vesta

    ``--source MITHNEOS --taxonomy L`` - All spectra of known L-types in MITHNEOS
    """

    idx = classy.index.load()
    idx_selected = pd.DataFrame()

    with st.expander(f"Query and select from {len(idx)} Spectra"):
        input = st.text_input(
            "Query the `classy` spectra database",
            value="",
            max_chars=None,
            key=None,
            type="default",
            help=HELP_INPUT,
            autocomplete=None,
            on_change=None,
            args=None,
            kwargs=None,
            placeholder="--source MITHNEOS --wave_min 0.4 --wave_max 2.4",
            disabled=False,
            label_visibility="visible",
        )

        # Live Update
        if input:
            ids, kwargs = parse_input(input)

            if ids:
                st.write(
                    f"Asteroid{'s' if len(ids)>1 else ''}: ",
                    ", ".join(f"`{id}`" for id in ids),
                )
            if kwargs:
                st.write(
                    "Criteria:", ", ".join(f"`{k}: {v}`" for k, v in kwargs.items())
                )

            id, kwargs = parse_input(input)
            idx = classy.index.query(id, **kwargs)
            idx["select"] = False
            idx = st.data_editor(
                idx,
                column_order=[
                    "select",
                    "name",
                    "number",
                    "wave_min",
                    "wave_max",
                    "shortbib",
                    "source",
                ],
                hide_index=True,
            )
            idx_selected = idx[idx.select]
        else:
            idx["select"] = False
            idx = st.data_editor(
                idx,
                column_order=[
                    "select",
                    "name",
                    "number",
                    "wave_min",
                    "wave_max",
                    "shortbib",
                    "source",
                ],
                hide_index=True,
            )

    if not idx_selected.empty:
        with st.expander(
            f"Selected {len(idx_selected)} spectr{'a' if len(idx_selected) != 1 else 'um'}."
        ):
            st.dataframe(
                idx_selected,
                column_order=[
                    "name",
                    "number",
                    "wave_min",
                    "wave_max",
                    "shortbib",
                    "source",
                ],
                hide_index=True,
            )

with right:
    if not idx_selected.empty:
        # Not setting target to avoid slow query
        # We just need name, number, albedo
        spectra_lit = classy.Spectra(
            classy.index.data.load_spectra(idx_selected, skip_target=True)
        )

        idx_selected = idx_selected.reset_index()
        for i, spec in enumerate(spectra_lit):
            spec.target = rocks.Rock(
                idx_selected["sso_name"].values[i],
                ssocard={
                    "name": idx_selected["name"].values[i],
                    "number": idx_selected["number"].values[i],
                    "parameters": {
                        "physical": {
                            "albedo": {"value": idx_selected["albedo"].values[i]}
                        }
                    },
                },
                skip_id_check=True,
            )

        p = figure(
            x_axis_label="Wavelength / μm",
            y_axis_label="Reflectance",
            toolbar_location="below",
            height=400,
        )

        colors = classy.plotting.get_colors(len(spectra_lit), cmap="Spectral")
        dashes = itertools.cycle(["solid", "dashed", "dotted", "dotdash", "dashdot"])

        legend_items = []
        for spec in spectra_lit:
            l = p.line(
                spec.wave,
                spec.refl,
                line_width=2,
                line_color=colors.pop(),
                line_dash=next(dashes),
            )
            legend_items.append((spec.name, [l]))
        p.add_layout(Legend(items=legend_items, location=(10, 210)))
        #
        # # TODO: Upload example file
        # # TODO: Possibility to enter target for each uploaded file
        # # TODO: Plot spectra as uploaded
        #
        st.bokeh_chart(p, use_container_width=True)

st.markdown("---")
st.header("Classify")

left, right = st.columns(2)

with left:
    st.markdown(
        "Click the button to classify the spectra in the taxonomic schemes of [Mahlke, DeMeo, and Tholen](https://classy.readthedocs.io/en/latest/taxonomies.html)."
    )
    st.markdown(f"Number of User Spectra: `{len(spectra_user)}`")
    st.markdown(f"Number of Literature Spectra: `{len(spectra_lit)}`")
    classify = st.button("Classify")

with right:
    if classify:
        if not spectra_lit and not spectra_user:
            st.write("You have to provide or select spectra first.")
        else:
            spectra = spectra_lit + list(spectra_user.values())
            spectra.classify()
            spectra.classify(taxonomy="demeo")
            spectra.classify(taxonomy="tholen")
            results = spectra.export(
                columns=[
                    "name",
                    "target.albedo.value",
                    "class_mahlke",
                    "class_demeo",
                    "class_tholen",
                ]
            )
            # st.write(", ".join(spec.class_ for spec in spectra))
            st.dataframe(results, hide_index=True)

st.markdown("---")
st.header("Visualize and Export")

st.write("To be implemented.")

# left, right = st.columns(2)
#
# with left:
#     st.markdown(
#         "Here, you can select spectra from the literature to include in your analysis."
#     )
#
# with right:
#     if st.button("Export"):
#         st.write("Exporting")

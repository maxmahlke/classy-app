import io
import os
import zipfile

import pandas as pd
import streamlit as st

# TODO: add rocks name-number index...

# classy and rocks need prior settings
os.environ["ROCKS_CACHE_DIR"] = "no-cache"
import rocks  # noqa


os.environ["CLASSY_DATA_DIR"] = "./data/"
import classy  # noqa

classy.config.APP_MODE = True

import literature
import plotting
import text  # noqa
import user

# ------
# Streamlit configuration
st.set_page_config(layout="wide")

# Init spectra session state entries
st.session_state["SPECTRA_USER"] = {}
st.session_state["SPECTRA_LIT"] = []

# ------
# Header
st.image(
    "https://raw.githubusercontent.com/maxmahlke/classy/master/docs/_static/logo_classy.png",
    width=100,
)

left, right = st.columns(2)

# with left:
st.markdown(text.GREETING)
st.markdown(text.INSTRUCTION)

# Using "with" notation
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/maxmahlke/classy/master/docs/_static/logo_classy.png",
        width=100,
    )

    st.markdown(
        "[GitHub](https://github.com/maxmahlke/classy) · [ReadTheDocs](https://classy.readthedocs.io/)"
    )
    st.text("")
    st.text("")
    st.text("In Short")

with st.sidebar:
    st.markdown("1. Upload your spectra")
    st.markdown("2. Add literature spectra")
    st.markdown("3. Classify spectra")
    st.markdown("4. Export classifications")

with st.sidebar:
    # st.markdown("[Upload your data](#Yourdata)")
    # st.markdown("Classify")
    # st.markdown("Plot and Export")

    st.text("")
    st.text("")
    st.text("")
    st.markdown("Development of `classy` and the web interface are on-going.")
    st.markdown("Last update: `2024-01-09`")
spectra = []
spectra_lit = []

# ------
# User data
user.layout()

# ------
# Literature data
st.markdown("---")
st.markdown("**Optional: Add literature spectra**")
left, right = st.columns(2)


with left:
    st.markdown(text.LITERATURE)

    # TODO: Make size of index more apparent, give more examples
    # "65k spectra, most common sources: SMASS, Gaia, most common shortbib: ..."
    # "most common asteroid: ..."
    # Make full width,

    idx = classy.index.load()
    idx_selected = pd.DataFrame()

    with st.expander(f"Query and select from {len(idx)} Spectra"):
        input = st.text_input(
            "Query the `classy` spectra database",
            value="",
            type="default",
            help=text.HELP_INPUT,
            placeholder="--source MITHNEOS --wave_min 0.4 --wave_max 2.4",
        )

        # Live Update
        if input:
            # TODO: --shortbib "Xu+ 1995" fails due to space
            # TODO: index contains my private spectra
            ids, kwargs = literature.parse_input(input)

            if ids:
                st.write(
                    f"Asteroid{'s' if len(ids)>1 else ''}: ",
                    ", ".join(f"`{id}`" for id in ids),
                )
            if kwargs:
                st.write(
                    "Criteria:", ", ".join(f"`{k}: {v}`" for k, v in kwargs.items())
                )

            idx = classy.index.query(ids, **kwargs)
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
            idx_selected = idx[idx.select]

    if not idx_selected.empty:
        # with st.sidebar:
        #     st.markdown(
        #         f"Selected {len(idx_selected)} spectr{'a' if len(idx_selected) != 1 else 'um'}."
        #     )
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

            # create in-memory zip file of spectra and summary csv
            b = io.BytesIO()
            zip = zipfile.ZipFile(b, mode="w")
            for file, meta in idx_selected.iterrows():
                if meta.source == "Gaia":
                    data = classy.sources.gaia._load_virtual_file(meta)
                    Path("data/" + file).parent.mkdir(parents=True, exist_ok=True)
                    data.to_csv("data/" + file, index=False)

                zip.write("data/" + file, file)

            idx_selected.to_csv("data/index.csv", index=True)
            zip.write("data/index.csv", "index.csv")
            zip.close()

            st.download_button("Download Spectra", b, mime="application/zip")

with right:
    if not idx_selected.empty:
        # Not setting target to avoid slow query
        # We just need name, number, albedo
        st.session_state.SPECTRA_LIT = classy.Spectra(
            classy.index.data.load_spectra(idx_selected, skip_target=True)
        )

        idx_selected = idx_selected.reset_index()
        for i, spec in enumerate(st.session_state.SPECTRA_LIT):
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

        plotting.plot_spectra("literature")
        #
        # # TODO: Upload example file
        # # TODO: Possibility to enter target for each uploaded file
        # # TODO: Plot spectra as uploaded
    user.update_session_spectra()

st.markdown("---")
st.markdown("**Classify**")

left, right = st.columns(2)

with left:
    # st.markdown(
    #     "Click the button to classify the spectra in the taxonomies of [Mahlke, DeMeo, and Tholen](https://classy.readthedocs.io/en/latest/taxonomies.html)."
    # )
    if st.session_state.SPECTRA_USER or st.session_state.SPECTRA_LIT:
        desc = f"Classify `{len(st.session_state.SPECTRA_USER) + len(st.session_state.SPECTRA_LIT)}` spectr{'um' if (len(st.session_state.SPECTRA_USER) + len(st.session_state.SPECTRA_LIT)) == 1 else 'a'}."
        classify = st.button(desc, disabled=False)
    else:
        classify = st.button("Classify", disabled=True)
        st.markdown(
            "Either upload your spectra or select literature spectra to continue."
        )

    # with right:
    if classify:
        if not st.session_state.SPECTRA:
            st.write("You have to provide or select spectra first.")
        else:
            with st.spinner("Classifying.."):
                spectra = st.session_state.SPECTRA
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

# st.markdown("---")
# st.markdown("**Visualize**")

with right:
    if classify:
        tab1, tab2, tab3 = st.tabs(["Mahlke+ 2022", "DeMeo+ 2009", "Tholen 1984"])

        with tab1:
            with st.spinner("Plotting  results"):
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots()
                classy.plotting._plot_taxonomy_mahlke(ax, spectra)
                st.pyplot(fig, dpi=600)

        with tab2:
            with st.spinner("Plotting  results"):
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots()
                classy.plotting._plot_taxonomy_demeo(ax, spectra)
                st.pyplot(fig, dpi=600)

        with tab3:
            # _, ax_tholen = spectra.plot(show=False, taxonomy="tholen")

            with st.spinner("Plotting  results"):
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots()
                classy.plotting._plot_taxonomy_tholen(ax, spectra)
                st.pyplot(fig, dpi=600)

# hide_footer_style = """
#     <style>
#     .reportview-container .main footer {visibility: hidden;}
#     """
# st.markdown(hide_footer_style, unsafe_allow_html=True)
# left, right = st.columns(2)
#
# with left:
#     st.markdown(
#         "Here, you can select spectra from the literature to include in your analysis."
#     )

# with right:
#     if st.button("Export"):
#         st.write("Exporting")
# #

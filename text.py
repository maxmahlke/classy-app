GREETING = (
    "Welcome to the web interface of `classy`, a tool for the analysis of asteroid reflectance spectra. "
    "This interface provides basic functionality. For the full feature set, you can have a look at the `python` package "
    "[here](https://classy.readthedocs.io)."
)

INSTRUCTION = (
    "This interface allows to visualise, classify, and export reflectance spectra and their metadata. You can provide your "
    "own data, use literature data, or a combination of the two. To get started, just keep scrolling."
)

# TODO: Upload example file
HELP_DATA_UPLOAD = """
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

TARGETS = (
    "For each spectrum, define the asteroidal target by providing an identifier. "
    "The benefits of doing so are described [here](https://classy.readthedocs.io/en/latest/core.html#assigning-a-target)."
)
def parse_input(args):
    """Separate identifiers and option key-value pairs from arguments."""

    # Separate query parameters and identifiers
    args = args.split()
    idx_options = [i for i, arg in enumerate(args) if arg.startswith("--")]
    kwargs = (
        {args[i].strip("--"): args[i + 1] for i in idx_options} if idx_options else {}
    )

    id = args[: min(idx_options)] if idx_options else args
    id = None if not id else id
    return id, kwargs

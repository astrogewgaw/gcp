if __name__ == "__main__":

    import re
    import copy

    from json import dump
    from requests import get
    from itertools import groupby
    from bs4 import BeautifulSoup  # type: ignore
    from typing import Dict, Tuple, Union, Optional

    clusters: Dict[
        str,
        Dict[
            str,
            Optional[
                Union[
                    str,
                    int,
                    Dict,
                    float,
                ]
            ],
        ],
    ] = {}

    tables = BeautifulSoup(
        get("http://www.naic.edu/~pfreire/GCpsr.html").content,
        "lxml",
    )("table")

    rows = tables[0]("tr")[2:]

    for i, row in enumerate(rows):
        cells = [_.text.strip() for _ in row("td")]
        clusters[str(i + 1)] = {
            key: (
                None
                if cell.strip() == "?"
                else conv(
                    cell.replace("−", "-").replace(">", "").replace("<", "").strip()
                )
            )
            for (key, conv), cell in zip(
                [
                    ("NAME", str),
                    ("R_CORE", float),
                    ("R_HL", float),
                    ("GL", float),
                    ("GB", float),
                    ("DIST", float),
                    ("NPSR", int),
                    ("NBINPSR", int),
                ],
                cells,
            )
        }

    rows = tables[1]("tr")[1:-1]

    clean = lambda _: (
        None
        if _.text.strip() in ("i", "*", "-", "")
        else _.text.replace("−", "-").replace(">", "").replace("<", "").strip()
    )

    def parser(value) -> Tuple[Optional[float], Optional[float]]:

        value = clean(value)

        if value is not None:
            regex = re.compile(r"\(([a-zA-Z]+|([0-9]*[.])?[0-9]+)\)?")
            match = re.search(regex, value)
            if match is not None:
                value = re.sub(regex, "", value)
                error = match.groups()[0]
                exponent = -1 * value.find(".")
                if re.search(r"×10-15", value):
                    scale = 1e-15 / 1e-20
                else:
                    scale = 1.0
                num_val = float(re.sub(r"×10-15", "", value)) * scale
                try:
                    num_err = float(error) * (10 ** exponent) * scale
                except:
                    num_err = None
            else:
                num_err = None
                if re.search(r"×10-15", value):
                    scale = 1e-15 / 1e-20
                else:
                    scale = 1.0
                num_val = float(re.sub(r"×10-15", "", value)) * scale
            return num_val, num_err
        else:
            return None, None

    cluster_pulsars = {
        clusters[str(i + 1)]["NAME"]: {
            str(j + 1): {
                key: conv(cell)  # type: ignore
                for (key, conv), cell in zip(
                    [
                        ("NAME", clean),
                        ("OFFSET", parser),
                        ("P0", parser),
                        ("P1", parser),
                        ("DM", parser),
                        ("PB", parser),
                        ("A1", parser),
                        ("ECC", parser),
                        ("MINMASS", parser),
                        ("NOTES", clean),
                        (
                            "REFS",
                            lambda _: [_["href"] for _ in _("a") if _["href"] != "#g"],
                        ),
                    ],
                    row,
                )
            }
            for j, row in enumerate(block)
        }
        for i, block in enumerate(
            [
                list(g)
                for k, g in groupby(
                    (_("td") for _ in rows),
                    lambda i: len(i),
                )
                if k
            ]
        )
    }

    copied = copy.deepcopy(cluster_pulsars)
    for name, pulsars in cluster_pulsars.items():
        for ix, pulsar in pulsars.items():
            for key, value in pulsar.items():
                if isinstance(value, tuple):
                    copied[name][ix][key] = value[0]
                    copied[name][ix][key + "_ERR"] = value[1]
    cluster_pulsars = copied

    with open("gcp.json", "w+") as fobj:
        dump(
            obj=dict(
                clusters=clusters,
                data=cluster_pulsars,
            ),
            fp=fobj,
            indent=4,
        )

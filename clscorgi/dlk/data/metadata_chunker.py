import json

from itertools import count

from importlib.resources.abc import Traversable
from importlib.resources import files

from more_itertools import ichunked


def generate_metadata_files():

    data_dir: Traversable = files("clscorgi.dlk.data")
    dlk_json_path: Traversable = data_dir / "dlk_full.json"
    cnt = count()

    with open(dlk_json_path) as f:
        dlk_json = json.load(f)

    _metadata = map(
        lambda entry: {
            "id": entry[0],
            "metadata": entry[1]["metadata"]
        },
        dlk_json.items()
    )

    dlk_chunks = ichunked(_metadata, 6000)

    for chunk in dlk_chunks:
        output_file = data_dir / f"dlk_metadata_{next(cnt)}.json"
        print(output_file)

        with open(output_file, "w") as f:
            f.write(json.dumps(list(chunk), indent=4))

if __name__ == "__main__":
    generate_metadata_files()

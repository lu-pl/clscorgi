![<img src="lodkit.png" width=10% height=10%>](https://raw.githubusercontent.com/lu-pl/clscorgi/main/clscorgi.jpg?token=GHSAT0AAAAAACKGOE4W5XCVJNLBM64NNJZEZODWU5A)

# CLSCorGI <📚>🐶

CLSCor Graph Integration - A place for conjuring CLSCor compliant RDF from various sources.

## Requirements

* Python >= 3.11

The script also expects a valid Github API token named "TOKEN" to be present in `.env`.

E.g. in `clscorgi/.env`: 
```text
TOKEN=<valid_github_api_token>
```

## Installation

Either use [poetry](https://python-poetry.org/) or activate a virtual environment (Python >=3.11) and run the following commands:
```shell
git clone git@github.com:lu-pl/clscorgi.git
cd clscorgi/
pip install .
```

## Modelling Notes

The gists listed below hold modelling examples and notes.

- ELTeC
  - [ELTeC CLSCor example](https://gist.github.com/lu-pl/83bf34d898b9a95a920133af38f524ab)

- ReM
  - [ReM modelling notes](https://gist.github.com/lu-pl/9ecf90094e6355e10a120b80229aa54c)
  - [ReM CLSCor example](https://gist.github.com/lu-pl/e96478123950719df0093ad9458720d3)

- Gutenberg
  - [Gutenberg modelling notes](https://gist.github.com/lu-pl/774837ec70943c5d30f3b7bd2901db30)

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

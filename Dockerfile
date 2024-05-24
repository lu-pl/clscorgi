FROM python:3.11.9
COPY ./ /veld/executable/
WORKDIR /veld/executable/
RUN pip install .


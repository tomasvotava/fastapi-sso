FROM dhermes/python-multi

WORKDIR /code

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:${PATH}"

RUN pip install tox

ADD . .

CMD ["tox"]

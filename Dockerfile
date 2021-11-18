FROM python:3.9

# install dependencies and update the system
RUN apt-get update && apt-get upgrade -y && pip install pipenv
COPY ./Pipfile.lock /opt/Pipfile.lock
COPY ./Pipfile /opt/Pipfile

WORKDIR /opt/
RUN pipenv install --deploy --ignore-pipfile --dev --system

# install the library
COPY ./fhir_kindling /opt/fhir_kindling
COPY ./tests /opt/tests
COPY ./setup.py /opt/setup.py
COPY ./.coveragerc /opt/coveragerc
COPY ./README.md /opt/README.md
COPY ./CHANGELOG.md /opt/CHANGELOG.md

RUN pip install .

CMD ["coverage", "run", "-m", "pytest", "tests"]

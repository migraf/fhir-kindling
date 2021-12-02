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

RUN pip install . && \
    curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh >> /opt/wait-for-it.sh && \
    chmod +x /opt/wait-for-it.sh

COPY ./scripts/container_coverage.sh /opt/container_coverage.sh

CMD ["/opt/wait-for-it.sh", "blaze-fhir:8080","--timeout=40", "--", "/opt/container_coverage.sh"]

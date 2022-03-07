import json

import pandas as pd
import pytest
import os

import xmltodict
from dotenv import load_dotenv, find_dotenv
from fhir.resources.condition import Condition
from fhir.resources.patient import Patient
from pydantic import ValidationError

from fhir_kindling import FhirServer
from fhir_kindling.fhir_query.query_parameters import FHIRQueryParameters, IncludeParameter, FieldParameter, \
    ReverseChainParameter, QueryOperators, QueryParameter


@pytest.fixture
def api_url():
    """
    Base api url and env vars
    """
    load_dotenv(find_dotenv())

    return os.getenv("FHIR_API_URL", "http://test.fhir.org/r4")


@pytest.fixture
def server(api_url):
    server = FhirServer(
        api_address=api_url,
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        oidc_provider_url=os.getenv("OIDC_PROVIDER_URL")
    )
    return server


@pytest.fixture
def paginated_xml():
    return """<?xml version="1.0" encoding="UTF-8"?>
<Bundle xmlns="http://hl7.org/fhir">
    <id value="C7GQWQ4ZM4OPHPS4"/>
    <type value="searchset"/>
    <total value="2283"/>
    <link>
        <relation value="self"/>
        <url value="http://localhost:9090/fhir/Patient?_count=50&amp;__t=57&amp;__page-id=C7E64KWQ6FOK7VH7"/>
    </link>
    <link>
        <relation value="next"/>
        <url value="http://localhost:9090/fhir/Patient?_count=50&amp;__t=57&amp;__page-id=C7E64KWQ6FOK7VJL"/>
    </link>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VH7"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VH7"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Carignan"/>
                    <given value="Mirac"/>
                </name>
                <gender value="female"/>
                <birthDate value="1999-11-01"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI2"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI2"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Lougheed"/>
                    <given value="Velmarie"/>
                </name>
                <gender value="male"/>
                <birthDate value="1969-12-01"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI3"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI3"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Solimeno"/>
                    <given value="Cobi"/>
                </name>
                <gender value="male"/>
                <birthDate value="1977-05-19"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI4"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI4"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Lester"/>
                    <given value="Shacoya"/>
                </name>
                <gender value="male"/>
                <birthDate value="1979-03-31"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI5"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI5"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kassin"/>
                    <given value="Ethian"/>
                </name>
                <gender value="male"/>
                <birthDate value="1967-05-17"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI6"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI6"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Weik"/>
                    <given value="Ernel"/>
                </name>
                <gender value="male"/>
                <birthDate value="1975-03-29"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VI7"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VI7"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Einhorn"/>
                    <given value="Kinsly"/>
                </name>
                <gender value="male"/>
                <birthDate value="1989-03-21"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIA"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIA"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kremers"/>
                    <given value="Jessican"/>
                </name>
                <gender value="male"/>
                <birthDate value="1934-06-15"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIB"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIB"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Weininger"/>
                    <given value="Amitava"/>
                </name>
                <gender value="female"/>
                <birthDate value="1925-10-04"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIC"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIC"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Nisly"/>
                    <given value="M'kai"/>
                </name>
                <gender value="female"/>
                <birthDate value="1995-03-01"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VID"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VID"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Mussell"/>
                    <given value="Rogerio"/>
                </name>
                <gender value="female"/>
                <birthDate value="1973-06-17"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIE"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIE"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Muszynski"/>
                    <given value="Natashya"/>
                </name>
                <gender value="male"/>
                <birthDate value="1923-02-08"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIF"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIF"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Soteros"/>
                    <given value="Keyshand"/>
                </name>
                <gender value="male"/>
                <birthDate value="1963-08-07"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIG"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIG"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Wayland"/>
                    <given value="Cellan"/>
                </name>
                <gender value="male"/>
                <birthDate value="1969-02-09"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIH"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIH"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Nemec"/>
                    <given value="Karolann"/>
                </name>
                <gender value="male"/>
                <birthDate value="1996-11-29"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VII"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VII"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Shadik"/>
                    <given value="Lizabet"/>
                </name>
                <gender value="male"/>
                <birthDate value="2003-02-10"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIJ"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIJ"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Farnese"/>
                    <given value="Blimie"/>
                </name>
                <gender value="male"/>
                <birthDate value="1990-01-25"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIK"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIK"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Gwilt"/>
                    <given value="Dur-e-mcknoon"/>
                </name>
                <gender value="male"/>
                <birthDate value="1995-09-15"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIL"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIL"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Bhanu"/>
                    <given value="Beckette"/>
                </name>
                <gender value="female"/>
                <birthDate value="1971-10-05"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIM"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIM"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kleppinger"/>
                    <given value="Austynn"/>
                </name>
                <gender value="female"/>
                <birthDate value="1945-05-05"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIN"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIN"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Umbach"/>
                    <given value="Mirabel"/>
                </name>
                <gender value="female"/>
                <birthDate value="1960-11-16"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIO"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIO"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Vishanu"/>
                    <given value="Mahraj"/>
                </name>
                <gender value="female"/>
                <birthDate value="1985-06-29"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIP"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIP"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Lauth"/>
                    <given value="Conaugh"/>
                </name>
                <gender value="other"/>
                <birthDate value="1937-02-04"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIQ"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIQ"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Samok"/>
                    <given value="Berendina"/>
                </name>
                <gender value="male"/>
                <birthDate value="1988-10-29"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIR"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIR"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kubasik"/>
                    <given value="Glinda"/>
                </name>
                <gender value="male"/>
                <birthDate value="1944-02-06"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIS"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIS"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Blas"/>
                    <given value="Tautiana"/>
                </name>
                <gender value="female"/>
                <birthDate value="1954-08-15"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIT"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIT"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Netto"/>
                    <given value="Emiri"/>
                </name>
                <gender value="female"/>
                <birthDate value="1948-06-21"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIU"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIU"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Dennin"/>
                    <given value="Sassa"/>
                </name>
                <gender value="female"/>
                <birthDate value="1976-04-26"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIV"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIV"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Fietek"/>
                    <given value="Dimitrios"/>
                </name>
                <gender value="female"/>
                <birthDate value="1933-06-05"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIW"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIW"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Pilarski"/>
                    <given value="Keiara"/>
                </name>
                <gender value="female"/>
                <birthDate value="1929-02-21"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIX"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIX"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Gillert"/>
                    <given value="Akalya"/>
                </name>
                <gender value="female"/>
                <birthDate value="1970-08-07"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIY"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIY"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Escalon"/>
                    <given value="Duric"/>
                </name>
                <gender value="female"/>
                <birthDate value="1954-02-08"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VIZ"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VIZ"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Altew"/>
                    <given value="Shelsey"/>
                </name>
                <gender value="male"/>
                <birthDate value="1936-05-24"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ2"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ2"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Schellenberge"/>
                    <given value="Breasia"/>
                </name>
                <gender value="female"/>
                <birthDate value="1954-03-23"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ3"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ3"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Durrwachter"/>
                    <given value="Litta"/>
                </name>
                <gender value="male"/>
                <birthDate value="1936-02-07"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ4"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ4"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Tsukamoto"/>
                    <given value="Jazmen"/>
                </name>
                <gender value="male"/>
                <birthDate value="1964-09-18"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ5"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ5"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kudlacik"/>
                    <given value="Rayonia"/>
                </name>
                <gender value="male"/>
                <birthDate value="1999-05-13"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ6"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ6"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Furrow"/>
                    <given value="Palvit"/>
                </name>
                <gender value="male"/>
                <birthDate value="2002-10-26"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJ7"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJ7"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Kelvin"/>
                    <given value="Darry"/>
                </name>
                <gender value="male"/>
                <birthDate value="1983-03-31"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJA"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJA"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Lebaron"/>
                    <given value="Kelashi"/>
                </name>
                <gender value="male"/>
                <birthDate value="1959-06-01"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJB"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJB"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Heersink"/>
                    <given value="Tamayia"/>
                </name>
                <gender value="female"/>
                <birthDate value="1946-12-22"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJC"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJC"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Quine"/>
                    <given value="Perreault"/>
                </name>
                <gender value="male"/>
                <birthDate value="1982-12-11"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJD"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJD"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Craton"/>
                    <given value="Alonnie"/>
                </name>
                <gender value="female"/>
                <birthDate value="1957-07-18"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJE"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJE"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Dilallo"/>
                    <given value="Linde"/>
                </name>
                <gender value="male"/>
                <birthDate value="1963-05-31"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJF"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJF"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Dolbeare"/>
                    <given value="Furiya"/>
                </name>
                <gender value="male"/>
                <birthDate value="1945-12-12"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJG"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJG"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Pattmon"/>
                    <given value="Crayson"/>
                </name>
                <gender value="male"/>
                <birthDate value="1933-11-28"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJH"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJH"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Carnighan"/>
                    <given value="Ellarose"/>
                </name>
                <gender value="male"/>
                <birthDate value="1956-12-27"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJI"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJI"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Whelihan"/>
                    <given value="Jonette"/>
                </name>
                <gender value="female"/>
                <birthDate value="1930-03-05"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJJ"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJJ"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Petropulos"/>
                    <given value="Zayn-ul-abidin"/>
                </name>
                <gender value="male"/>
                <birthDate value="1930-10-28"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
    <entry>
        <fullUrl value="http://localhost:9090/fhir/Patient/C7E64KWQ6FOK7VJK"/>
        <resource>
            <Patient>
                <id value="C7E64KWQ6FOK7VJK"/>
                <meta>
                    <versionId value="27"/>
                    <lastUpdated value="2021-10-20T18:07:08.130Z"/>
                </meta>
                <name>
                    <family value="Ducci"/>
                    <given value="Kratsas"/>
                </name>
                <gender value="male"/>
                <birthDate value="1987-10-05"/>
            </Patient>
        </resource>
        <search>
            <mode value="match"/>
        </search>
    </entry>
</Bundle>
"""


"""
########################################################################################################################
Test Query Parameters
########################################################################################################################
"""


def test_query_param_abstract():
    query_param = QueryParameter()
    with pytest.raises(NotImplementedError):
        query_param.to_url_param()

    with pytest.raises(NotImplementedError):
        param = QueryParameter.from_url_param("sdada")


def test_field_query_param():
    resource = "Patient"
    field_param = FieldParameter(
        **dict(
            field="active",
            value=True,
            operator=QueryOperators.eq
        )
    )

    assert field_param.to_url_param() == "active=true"

    field_param = FieldParameter(
        **dict(
            field="active",
            value=["hello", "world"],
            operator=QueryOperators.in_
        )
    )

    assert field_param.to_url_param() == "active=hello,world"

    value = 7.3213
    field_param = FieldParameter(
        **dict(
            field="active",
            value=value,
            operator=QueryOperators.gt
        )
    )
    assert field_param.to_url_param() == f"active=gt{value}"

    # list value arg without in operator should fail
    with pytest.raises(ValidationError):
        field_param = FieldParameter(
            **dict(
                field="active",
                value=["hello", "world"],
                operator=QueryOperators.eq
            )
        )

    # in operator only for list value arg
    with pytest.raises(ValidationError):
        field_param = FieldParameter(
            **dict(
                field="active",
                value="hello",
                operator=QueryOperators.in_
            )
        )
    with pytest.raises(ValidationError):
        field_param = FieldParameter(
            **dict(
                field="active",
                value=[32, "sdsa".encode()],
                operator=QueryOperators.in_
            )
        )

    # operator not included in enum
    with pytest.raises(ValidationError):
        field_param = FieldParameter(
            field="active",
            operator="hello",
            value=True
        )

    # parameter generation from url snippet

    param_from_url = FieldParameter.from_url_param("active=true")

    assert param_from_url.field == "active"
    assert param_from_url.operator == QueryOperators.eq
    assert isinstance(param_from_url.value, bool)
    assert param_from_url.value is True

    # list of search params
    param_from_url = FieldParameter.from_url_param("active=hello,world")

    assert param_from_url.field == "active"
    assert param_from_url.operator == QueryOperators.in_
    assert param_from_url.value == ["hello", "world"]

    # integer value
    param_from_url = FieldParameter.from_url_param("integer=gt7")
    assert param_from_url.field == "integer"
    assert param_from_url.operator == QueryOperators.gt
    assert isinstance(param_from_url.value, int)
    assert param_from_url.value == 7

    # float value
    param_from_url = FieldParameter.from_url_param("float=7.3213")
    assert param_from_url.field == "float"
    assert param_from_url.operator == QueryOperators.eq
    assert param_from_url.value == 7.3213

    # list of numbers
    param_from_url = FieldParameter.from_url_param("integers=7,8")
    assert param_from_url.field == "integers"
    assert param_from_url.operator == QueryOperators.in_
    assert param_from_url.value == [7, 8]


def test_include_query_param():
    resource = "Condition"
    search_param = "subject"
    target = "test"

    # conversion to url strings

    # basic include
    include_param = IncludeParameter(
        resource=resource,
        search_param=search_param,
    )
    assert include_param.to_url_param() == f"_include={resource}:{search_param}"

    # with target
    include_param = IncludeParameter(
        resource=resource,
        search_param=search_param,
        target=target
    )
    assert include_param.to_url_param() == f"_include={resource}:{search_param}:{target}"

    # reverse include
    include_param = IncludeParameter(
        resource=resource,
        search_param=search_param,
        target=target,
        reverse=True
    )
    assert include_param.to_url_param() == f"_revinclude={resource}:{search_param}:{target}"

    # include with iterate & target
    include_param = IncludeParameter(
        resource=resource,
        search_param=search_param,
        target=target,
        iterate=True,
    )

    assert include_param.to_url_param() == f"_include:iterate={resource}:{search_param}:{target}"

    # parse from url snippet

    include_param = IncludeParameter.from_url_param(f"_include={resource}:{search_param}")
    assert include_param.resource == resource
    assert include_param.search_param == search_param

    include_param = IncludeParameter.from_url_param(f"_include={resource}:{search_param}:{target}")
    assert include_param.resource == resource
    assert include_param.search_param == search_param
    assert include_param.target == target

    include_param = IncludeParameter.from_url_param(f"_revinclude={resource}:{search_param}:{target}")
    assert include_param.resource == resource
    assert include_param.search_param == search_param
    assert include_param.target == target
    assert include_param.reverse is True

    include_param = IncludeParameter.from_url_param(f"_include:iterate={resource}:{search_param}:{target}")
    assert include_param.resource == resource
    assert include_param.search_param == search_param
    assert include_param.target == target
    assert include_param.iterate is True

    with pytest.raises(ValueError):
        include_param = IncludeParameter.from_url_param(f"_include:iterates={resource}:{search_param}:{target}")

    with pytest.raises(ValueError):
        include_param = IncludeParameter.from_url_param(f"_include:iterates={resource}:{search_param}:{target}:error")


def test_reverse_chain_parameters():
    resource = "Condition"
    reference_param = "patient"
    search_param = "code"
    value = "test"
    query_url = f"_has:{resource}:{reference_param}:{search_param}=test"
    chain_param = ReverseChainParameter(
        resource=resource,
        reference_param=reference_param,
        search_param=search_param,
        operator=QueryOperators.eq,
        value=value
    )

    assert chain_param.to_url_param() == query_url

    param_from_url = ReverseChainParameter.from_url_param(query_url)

    assert param_from_url.resource == chain_param.resource

    query_url = f"_has:{resource}:{reference_param}:{search_param}=netest,test2"
    param_from_url = ReverseChainParameter.from_url_param(query_url)
    assert param_from_url.value == ["test", "test2"]
    assert param_from_url.operator == QueryOperators.not_in


def test_fhir_query_parameters():
    query_params = FHIRQueryParameters(
        resource="Condition"
    )
    assert query_params.to_query_string() == "/Condition?"

    # invalid resource name
    with pytest.raises(ValidationError):
        query_params = FHIRQueryParameters(
            resource="Conditionkdjsaldj"
        )

    url = "/Patient?"
    query_params = FHIRQueryParameters.from_query_string(url)

    assert query_params.resource == "Patient"

    query_url = "/Condition?code=test&_include=Condition:patient&_has:Patient:subject:age=gt:18"
    query_params = FHIRQueryParameters.from_query_string(query_url)

    assert query_params.to_query_string() == query_url


"""
########################################################################################################################
Test query conditions and execution
########################################################################################################################
"""


def test_query_xml(server):
    resp = server.query("Patient", output_format="xml")
    result = resp.limit(100)

    assert result.response
    assert isinstance(result.response, str)

    with pytest.raises(NotImplementedError):
        includes = result.included_resources


def test_query_json(server):
    resp = server.query("Patient", output_format="json")
    result = resp.limit(100)
    assert result.response
    assert isinstance(result.response, dict)

    includes = result.included_resources
    assert not includes

def test_query_first(server):
    query = server.query("Patient")
    result = query.first()

    assert len(result.resources) == 1
    assert isinstance(result.resources[0], Patient)


def test_query_limit(server):
    query = server.query("Patient")
    query._count = 30
    result = query.limit(100)
    assert len(result.resources) == 100


def test_query_response_resources(server):
    query = server.query("Patient")
    result = query.all()

    assert len(result.resources) >= 1
    assert isinstance(result.resources[0], Patient)


def test_set_query_string(server, api_url):
    query_resource = "Condition"
    search_param = "subject"

    query = server.query(query_resource)
    query_string = f"/{query_resource}?_include={query_resource}:{search_param}"

    query.set_query_string(query_string)
    query_url = f"{api_url}/{query_resource}?_include={query_resource}:{search_param}&_count=5000&_format=json"
    assert query.query_url == query_url


def test_query_where(server):
    query_resource = "Patient"

    query = server.query(query_resource)

    with pytest.raises(ValueError):
        query.where(field_param="jdsha", filter_dict={"jdsh": "jdsh"})

    with pytest.raises(ValueError):
        query.where()

    with pytest.raises(ValueError):
        query.where(field_param="jdsha", field="dsad")

    with pytest.raises(ValueError):
        query.where(field="jdsha", filter_dict={"jdsh": "jdsh"})

    assert query.resource.resource_type == query_resource

    param = FieldParameter(
        field="name",
        operator=QueryOperators.eq,
        value="test"
    )

    param_dict = dict(
        field="name",
        operator="gt",
        value="test"
    )

    query = query.where(field_param=param)

    assert len(query.query_parameters.resource_parameters) == 1
    assert query.query_parameters.resource_parameters[0].field == "name"

    query = query.where(filter_dict=param_dict)

    assert len(query.query_parameters.resource_parameters) == 2
    assert query.query_parameters.resource_parameters[1].field == "name"
    assert query.query_parameters.resource_parameters[1].operator == QueryOperators.gt

    query = query.where(field="name", operator="lt", value="test")

    assert len(query.query_parameters.resource_parameters) == 3
    assert query.query_parameters.resource_parameters[2].field == "name"
    assert query.query_parameters.resource_parameters[2].operator == QueryOperators.lt

    query = query.where(field="name", operator=QueryOperators.lt, value="test")

    assert len(query.query_parameters.resource_parameters) == 4
    assert query.query_parameters.resource_parameters[2].field == "name"
    assert query.query_parameters.resource_parameters[2].operator == QueryOperators.lt

    with pytest.raises(ValueError):
        query = query.where(field="name", operator="fails", value="test")

    with pytest.raises(ValueError):
        query = query.where(field="name", operator=67321.21, value="test")

    # with pytest.raises(ValueError):
    query = query.where(field="name", operator=QueryOperators.eq, value="test")

    with pytest.raises(ValueError):
        query = query.where(field="name", value="test")

    with pytest.raises(ValidationError):
        param_dict = dict(
            field="name",
            operator="fails",
            value="test"
        )
        query = query.where(filter_dict=param_dict)

    print(query.query_url)

    # execute a valid query
    valid_query_param = FieldParameter(
        field="birthdate",
        operator=QueryOperators.gt,
        value="1930-01-01"
    )
    query = server.query("Patient")
    query = query.where(field_param=valid_query_param)

    response = query.all()

    assert response


def test_query_include(server, api_url):
    query_resource = "Condition"
    search_param = "subject"

    query = server.query(query_resource)

    with pytest.raises(ValueError):
        query = query.include()

    query = query.include(resource=query_resource, reference_param=search_param)

    assert query.query_parameters.include_parameters[0].resource == query_resource

    query_url = f"{api_url}/{query_resource}?_include={query_resource}:{search_param}&_count=5000&_format=json"
    print(query.query_url)
    assert query.query_url == query_url

    include_param = IncludeParameter(
        resource=query_resource,
        search_param=search_param,
        target="criteria",
        reverse=True
    )

    query = query.include(include_param=include_param)
    print(query)
    assert query.query_parameters.include_parameters[1].resource == query_resource
    assert query.query_parameters.include_parameters[1].target == "criteria"

    include_dict = dict(
        resource=query_resource,
        search_param=search_param,
        target="hello",
        reverse=False
    )

    query = query.include(include_dict=include_dict)
    assert query.query_parameters.include_parameters[2].resource == query_resource
    assert query.query_parameters.include_parameters[2].target == "hello"

    with pytest.raises(ValueError):
        query = query.include(include_param=include_param, resource=query_resource)

    with pytest.raises(ValueError):
        query = query.include(include_dict=include_dict, resource=query_resource)

    with pytest.raises(ValueError):
        query = query.include(include_param=include_param, include_dict=include_dict)


def test_query_reverse_chain(server, api_url):
    has_resource = "Condition"
    reference_param = "subject"
    search_param = "code"
    operator = QueryOperators.eq
    value = "test"

    query = server.query("Patient")

    query = query.has(resource=has_resource, reference_param=reference_param, search_param=search_param,
                      operator=operator, value=value)

    assert query

    has_param = ReverseChainParameter(
        resource=has_resource,
        reference_param=reference_param,
        search_param=search_param,
        operator=operator,
        value=7
    )

    has_param_dict = dict(
        resource=has_resource,
        reference_param=reference_param,
        search_param=search_param,
        operator=QueryOperators.in_,
        value=["test1", "test2"]
    )

    query = query.has(has_param=has_param)
    assert query.query_parameters.has_parameters[1].resource == has_resource
    assert query.query_parameters.has_parameters[1].value == 7

    query = query.has(has_param_dict=has_param_dict)

    assert query.query_parameters.has_parameters[2].resource == has_resource
    assert query.query_parameters.has_parameters[2].operator == QueryOperators.in_
    assert query.query_parameters.has_parameters[2].value == ["test1", "test2"]

    with pytest.raises(ValueError):
        query = query.has(has_param=has_param, has_param_dict=has_param_dict)

    with pytest.raises(ValueError):
        query = query.has(has_param=has_param, resource="test")

    with pytest.raises(ValueError):
        query = query.has(resource="has_param", has_param_dict=has_param_dict)

    with pytest.raises(ValueError):
        query = query.has()


"""
########################################################################################################################
Test Query Response
########################################################################################################################
"""


def test_query_response(server):
    query_resource = "Patient"

    query = server.query(query_resource)
    query._count = 50

    response = query.all()

    assert len(response.resources) >= 2
    assert response.resources[0].resource_type == query_resource


def test_query_response_include(server):
    query_resource = "Condition"
    search_param = "subject"

    query = server.query(query_resource)

    with pytest.raises(ValueError):
        query = query.include()

    query = query.include(resource=query_resource, reference_param=search_param)
    response = query.all()

    print(query)
    assert response.included_resources
    assert response.resources
    assert response.resources[0].resource_type == query_resource


def test_query_response_save(server):
    xml_file = "test_query_response_save.xml"
    json_file = "test_query_response_save.json"
    csv_file = "test_query_response_save.csv"

    # test saving single resource and xml
    query_resource = "Condition"
    query = server.query(query_resource, output_format="xml")
    response = query.limit(100)
    response.save(xml_file, format="xml")

    with pytest.raises(NotImplementedError):
        response.save(xml_file, format="json")

    assert os.path.isfile(xml_file)
    assert xmltodict.parse(open(xml_file, "r").read()) == xmltodict.parse(response.response)

    os.remove(xml_file)

    # invalid format
    with pytest.raises(ValueError):
        response.save(xml_file, format="invalid")

    # test with included resources and json
    query_resource = "Condition"
    search_param = "subject"

    query = server.query(query_resource)

    with pytest.raises(ValueError):
        query = query.include()

    query = query.include(resource=query_resource, reference_param=search_param)
    response = query.all()

    response.save(json_file, format="json")

    assert os.path.isfile(json_file)
    assert json.loads(open(json_file).read())

    os.remove(json_file)

    # save to csv
    patient_response = server.query("Patient").all()
    patient_response.save(csv_file, format="csv")

    assert os.path.isfile(csv_file)
    assert pd.read_csv(csv_file).shape[0] > 0

    # os.remove(csv_file)

    # save to csv with included resource
    response.save(csv_file, format="csv")

    assert os.path.isfile(csv_file)
    assert pd.read_csv(csv_file).shape[0] > 0

    included_patients_csv = "test_query_response_save_included_Patient.csv"
    assert os.path.isfile(included_patients_csv)
    assert pd.read_csv(included_patients_csv).shape[0] > 0

    os.remove(csv_file)
    os.remove(included_patients_csv)


def test_query_response_to_dfs(server):
    # test with included resources and json
    query_resource = "Condition"
    search_param = "subject"

    query = server.query(query_resource)

    with pytest.raises(ValueError):
        query = query.include()

    query = query.include(resource=query_resource, reference_param=search_param)
    response = query.all()

    with pytest.raises(ValueError):
        response.to_dfs(format="invalid")

    dfs = response.to_dfs()

    assert len(dfs) > 1
    assert dfs[0].shape[0] > 0

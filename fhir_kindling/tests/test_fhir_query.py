import pytest
import os
from dotenv import load_dotenv, find_dotenv

from fhir_kindling.fhir_query import FHIRQuery
from fhir_kindling import FhirServer
import xmltodict


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


def test_query_xml(server):
    resp = server.query("Patient", output_format="xml")
    result = resp.all()
    assert result.response
    assert isinstance(result.response, str)


def test_query_json(server):
    resp = server.query("Patient", output_format="json")
    result = resp.all()
    assert result.response
    assert isinstance(result.response, dict)

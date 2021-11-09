from requests import Session


def get_server_summary(session: Session, base_url: str) -> dict:
    """
    Get server summary from FHIR server.
    """
    response = session.get(base_url + '/metadata')
    if response.status_code == 200:
        return response.json()
    else:
        return None

import json
import os
import uuid
from itertools import islice
from pathlib import Path
from typing import List

import certifi
import numpy as np
import streamlit as st
from openai import AzureOpenAI
from requests.structures import CaseInsensitiveDict

APP_SERVICE_FOUNDRY_ACCESS_TOKEN_HEADER = "X-Foundry-AccessToken"
APP_SERVICE_SNOWFLAKE_ACCESS_TOKEN_HEADER = "X-Snowflake-AccessToken"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MERCK_ROOT_CA = """-----BEGIN CERTIFICATE-----
MIIGOzCCBCOgAwIBAgIQHt22MoeoebZLg1n5IiALWTANBgkqhkiG9w0BAQsFADBT
MQswCQYDVQQGEwJERTEUMBIGA1UECgwLTWVyY2sgR3JvdXAxEzARBgNVBAsMCk1l
cmNrIEtHYUExGTAXBgNVBAMMEE1FUkNLIFJPT1QgQ0EgMDEwHhcNMTYxMDI4MDg1
MjU2WhcNMzYxMDI4MDkwMjUyWjBTMQswCQYDVQQGEwJERTEUMBIGA1UECgwLTWVy
Y2sgR3JvdXAxEzARBgNVBAsMCk1lcmNrIEtHYUExGTAXBgNVBAMMEE1FUkNLIFJP
T1QgQ0EgMDEwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQDQGa8XIrc9
Ri5hhJfXHCfzbJY9sueLJXtOuwYdGD/riltHGCOitOxFGCTTwelCDwpvT+9VB0rM
tbtU5pZMNhWhPm+6xVG0pBOsZW65sL+rgh9o4kvSfAmLE7n8qZmek1jfK/i8tRHI
D51YM+1+ObBcrCi5KrqROEpJEvGIQjbaKM6kCuhJGGcxr40gQ1hc4mVysRELOv4y
8YU3bSHiqDpMvwzCD+57xuYSfuZx6YXSfPXM1JU6vjZ1fp3NjbArp9+Ml9b4UC7Q
FInGmwRhEmd1UMdDm2IshhOlQ8Q4NXoOdecrQCkyHKHKpvvolDmnpucdUa8hVrDq
Xk94r/AEbIk87OBjl9r/V2ei7lD45pjanam24Xm5uwJDX2RrL+LxD4tNQTDig/f5
F75hSPHWsFatQrxT2mNtOihfAFWZySTzVTNE+Ez3nei0GZ92QcdX3jn0oTvezGEn
cnSp9mhGnWlXUXQ5GXEIUsF3Krvkw30xSM1tJt7tpnAR8ZIqBFcfhdVuNnhSZvzS
qoxBEEf2N76k28rCq/PuxcAd0EwE5x7eDcD7ZNjLev/wgqthUv+zddkKlfhRWop7
Z7hmvQRYWp9mOqX0t6B6y0/ulAqgn67U7qb/XzpnvVp5Aydv1tQ+qq6Od1JlMScj
nv0F7KSTrnc5K8KPsSFxOkcNkoCMdVgGzQIDAQABo4IBCTCCAQUwDgYDVR0PAQH/
BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFNDmVlzqHY/5Kj0GGKWU
kZwA1VUzMIHCBgNVHSAEgbowgbcwgbQGBFUdIAAwgaswgagGCCsGAQUFBwICMIGb
HoGYAEMAZQByAHQAaQBmAGkAYwBhAHQAaQBvAG4AIABQAHIAYQBjAHQAaQBjAGUA
IABTAHQAYQB0AGUAbQBlAG4AdAAgACgAQwBQAFMAKQAgAGEAdgBhAGkAbABhAGIA
bABlACAAbwBuACAAcgBlAHEAdQBlAHMAdAAgAGYAcgBvAG0AIABJAFQAIABTAGUA
YwB1AHIAaQB0AHkwDQYJKoZIhvcNAQELBQADggIBADaPFSRRqFU9Uu8xEgk7rxJt
XHoVnMoDiHhHcTBeG+9U3q1tSA/MohIPZN98isEP6BLlN2tv5xVZRG8VjmIj3bE5
KUcwSNKRPUYZHIelTkXZnyfjnWLG1aFloLmnysZOQcK/ce/uRTIeivGPIneJgifs
NTeYZF7b5WYAGtkTC5t+TFdAxVw4ptmwX1NDgAwclUE72JxtDk8xPxYfy/26vA6+
Rfl3YaRiwB++WxUaG68wYHWV4+uo6enz0NIJwvlg+4sZGCeoQ/zRl1yQM4sBu3DT
uYVoN15MAnrxbXJ81LSrCYJGLNM1pbA75a3UwTercGoCh0gchLuuCWk8vz3TmkU2
xZRGVpqFveoO4Y2Gd08QMJBSRmCaCmaDFUqbqPump/euTbjPICTZ0gEn9SfhAVWK
dotKAz7yqhrjOx08x3fBtbggnLvQrK1NBgsXUz6+c2WcqVh1yR9DCYqLSW656psv
J42zE5cplnkhc+0XS7itIaBwEEHR6XDq006YZpQeYapSAZ5F+Vc782UGQa+4fFg2
0rkON71IUxOG6rsVG85Fnt4xPAIHxJxMT4FKKlN0yFxc4aBn8Mj/GRP9up0caUoF
lmIhWZaOkQFhYXt7TGNzYxf2FUM1OVZetlF8cIX29LoqzSVYIT6kJVoO/+JnKjqv
1U8Ol3yI5k05mg+n+Tac
-----END CERTIFICATE-----
"""


def _create_cacert_bundle_with_merck_additions() -> str:
    """
    Takes certifi's cacert bundle, adds Merck Root CA and Merck ssl decryption
    certificate and returns the path to the combined cacert.pem file.

    Returns: the path to the combined cacert.pem file.
    """
    ca_certs = Path(certifi.where()).read_text(encoding="UTF-8")
    cacert_path = PROJECT_ROOT / "cacert.pem"
    with cacert_path.open("w") as f:
        f.write(ca_certs)
        f.write('\n# Label: "MERCK ROOT CA 01"\n')
        f.write(MERCK_ROOT_CA)
    return str(cacert_path.absolute())


def create_embeddings_batch(
    client: AzureOpenAI,
    texts: List[str],
    embedding_model_name: str = "text-embedding-ada-002-v2",
) -> np.ndarray:
    resp = client.embeddings.create(model=embedding_model_name, input=texts)
    return np.stack([e.embedding for e in resp.data], axis=0)


# copied from: https://docs.python.org/3.12/library/itertools.html#itertools.batched
def batched(iterable, n):
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def get_streamlit_request_headers():
    """Helper function that returns streamlit request headers.

    This implementation works starting with streamlit>=1.14.0

    Returns:
        :py:class:`~requests.structures.CaseInsensitiveDict`:
            case-insensitive dict with request headers
    """
    from streamlit import context

    return CaseInsensitiveDict(context.headers.to_dict())


def show_code(file_path):
    with open(file_path, "r") as f:
        own_code = f.read()

    with st.expander("Show Source Code of this page"):
        st.code(own_code, language="python")


def app_is_running_on_app_service() -> bool:
    return True if "APP_SERVICE_TS" in os.environ else False


def api_key_is_valid_uuid(api_key: str) -> bool:
    """Check if the API key is a valid UUID.

    Args:
        api_key (str): API key to check.

    Returns:
        bool: True if the API key is a valid UUID, False otherwise.
    """
    try:
        uuid.UUID(api_key)
        return True
    except ValueError:
        return False


def setup_environment() -> None:
    """Sets up the necessary environment variables for the application.

    This function should be called before the application initializes. It configures
     environment variables for running the application.
    For local development it ensures that:
    - The application configuration is loaded from 'config.json'
    - The requests and httpx libraries are configured to use the Merck SSL certificates
    When running in the app service in ensures that:
    - If the user provides a runtime configuration through the app service console, then
      each configured json entry is exposed as environment variables.
    """
    if not app_is_running_on_app_service():
        path_config = PROJECT_ROOT / "config.json"
        try:
            os.environ["APP_SERVICE_CONFIG"] = Path(path_config).read_text()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Missing config.json. Please duplicate the config-template.json file and fill with your own credentials."
            ) from e

        # local development requires certificate / ssl setup
        cacert_path = _create_cacert_bundle_with_merck_additions()
        # The httpx library used by openai uses SSL_CERT_FILE environment variable:
        # https://www.python-httpx.org/compatibility/#ssl-configuration
        os.environ["SSL_CERT_FILE"] = cacert_path
        # The requests library uses the REQUESTS_CA_BUNDLE environment variable:
        # https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
        os.environ["REQUESTS_CA_BUNDLE"] = cacert_path

    # In appservice, APP_SERVICE_CONFIG is present when the user provides a runtime
    # configuration through the app service console
    if "APP_SERVICE_CONFIG" in os.environ:
        config = json.loads(os.environ["APP_SERVICE_CONFIG"])
        os.environ.update(config)


@st.cache_resource
def create_openai_client(
    api_version: str = "2024-02-01",
) -> AzureOpenAI:
    """Wrap client creation into singleton to avoid re-creation of the client on re-runs.
    If you want to adjust the api key or endpoint, control it via the
    APP_SERVICE_NLP_API_URL and APP_SERVICE_NLP_API_KEY environment variables.

    Args:
        api_version (str, optional): API version. Defaults to "2024-02-01".

    Returns:
        AzureOpenAI: Azure OpenAI client.
    """
    # HACK: The default APP_SERVICE_NLP_API_URL injected into a deployed apps environment
    # ends with a trailing slash '/'. The AzureOpenAI client does not resolve this and incorrectly
    # sets up the URLs for the API calls. As a workaround, we need to remove the trailing slash if present.
    azure_endpoint = str(os.getenv("APP_SERVICE_NLP_API_URL", "")).rstrip("/")
    api_key = os.getenv("APP_SERVICE_NLP_API_KEY", "")
    if not api_key_is_valid_uuid(api_key):
        raise ValueError(
            "APP_SERVICE_NLP_API_KEY environment variable invalid. Please look at the "
            "'Configure the app' section in the README.md for a step-by-step guide"
        )

    return AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_version=api_version,
        api_key=api_key,
    )

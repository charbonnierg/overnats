import tempfile
from pathlib import Path

import pytest
import trustme


@pytest.fixture
def organization_name():
    return "easynats"


@pytest.fixture
def organization_unit_name():
    return "testing"


@pytest.fixture
def tls_key_type():
    return "ECDSA"


@pytest.fixture
def certificate_authority(
    organization_name: str,
    organization_unit_name: str,
    tls_key_type: str,
):
    if tls_key_type == "ECDSA":
        key_type = trustme.KeyType.ECDSA
    elif tls_key_type == "RSA":
        key_type = trustme.KeyType.RSA
    else:
        raise TypeError(f"Invalid tls_key_type: {tls_key_type}")
    return trustme.CA(
        organization_name=organization_name,
        organization_unit_name=organization_unit_name,
        key_type=key_type,
    )


@pytest.fixture
def server_identity():
    return "test-server.example.org"


@pytest.fixture
def server_certificate(certificate_authority: trustme.CA, server_hostname: str):
    return certificate_authority.issue_cert(server_hostname)


@pytest.fixture
def ca_crt(certificate_authority: trustme.CA):
    with tempfile.TemporaryDirectory() as d:
        filepath = Path(d).joinpath("ca.crt")
        filepath.write_bytes(certificate_authority.cert_pem.bytes())
        yield filepath.as_posix()


@pytest.fixture
def ca_key(certificate_authority: trustme.CA, ca_crt: str):
    filepath = Path(ca_crt).parent.joinpath("ca.key")
    filepath.write_bytes(certificate_authority.private_key_pem.bytes())
    return filepath.as_posix()


@pytest.fixture
def server_crt(server_certificate: trustme.LeafCert):
    with tempfile.TemporaryDirectory() as d:
        filepath = Path(d).joinpath("server.crt")
        filepath.write_bytes(
            b"\n".join(chain.bytes() for chain in server_certificate.cert_chain_pems)
        )
        yield filepath.as_posix()


@pytest.fixture
def server_key(server_certificate: trustme.LeafCert, server_crt: str):
    filepath = Path(server_crt).parent.joinpath("server.key")
    filepath.write_bytes(server_certificate.private_key_pem.bytes())
    return filepath.as_posix()


@pytest.fixture
def client_identity():
    return "test-client.example.org"


@pytest.fixture
def client_certificate(certificate_authority: trustme.CA, client_identity: str):
    return certificate_authority.issue_cert(client_identity)


@pytest.fixture
def client_crt(client_certificate: trustme.LeafCert):
    with tempfile.TemporaryDirectory() as d:
        filepath = Path(d).joinpath("client.crt")
        filepath.write_bytes(
            b"\n".join(chain.bytes() for chain in client_certificate.cert_chain_pems)
        )
        yield filepath.as_posix()


@pytest.fixture
def client_key(client_certificate: trustme.LeafCert, client_crt: str):
    filepath = Path(client_crt).parent.joinpath("client.key")
    filepath.write_bytes(client_certificate.private_key_pem.bytes())
    return filepath.as_posix()


@pytest.fixture
def temporary_file():
    with tempfile.TemporaryDirectory() as d:
        filepath = Path(d).joinpath("temporary")
        filepath.touch()
        yield filepath.as_posix()


@pytest.fixture
def nkey_file():
    with tempfile.TemporaryDirectory() as d:
        filepath = Path(d).joinpath("nkey")
        Path(filepath).write_text(
            "SUACSSL3UAHUDXKFSNVUZRF5UHPMWZ6BFDTJ7M6USDXIEDNPPQYYYCU3VY"
        )
        yield filepath.as_posix()

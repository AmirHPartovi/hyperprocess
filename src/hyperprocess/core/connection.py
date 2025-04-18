from __future__ import annotations
import sys
import socket
import time
from pathlib import Path
from typing import Any, Optional, Tuple, Union
import secrets
import hmac
import logging
import multiprocessing.connection as mp_conn
from multiprocessing import AuthenticationError

logger = logging.getLogger(__name__)
BUFSIZE = 8192

# Windows-specific imports (hidden from static checkers)
if sys.platform == 'win32':
    import multiprocessing._multiprocessing as _mp  # type: ignore[import]
    PipeListener = _mp.PipeListener          # type: ignore[attr-defined]
    PipeConnection = _mp.PipeConnection      # type: ignore[attr-defined]


def arbitrary_address(family: str) -> Union[tuple[str, int], Path, str]:
    """
    Return an arbitrary free address for the given family.
    """
    if family == 'AF_INET':
        return ('localhost', 0)
    if family == 'AF_UNIX':
        base = Path.home() / ".hyperprocess"
        base.mkdir(parents=True, exist_ok=True)  # ensure directory exists
        return base / f"listener-{int(time.time()*1000)}.sock"
    if family == 'AF_PIPE':
        return fr"\\.\pipe\hyperprocess-{secrets.token_hex(8)}"
    raise ValueError(f'Unrecognized family: {family}')


def address_type(addr: Any) -> str:
    """
    Infer address family from an address object.
    """
    if isinstance(addr, tuple):
        return 'AF_INET'
    if isinstance(addr, Path):
        return 'AF_UNIX'
    if isinstance(addr, str) and addr.startswith(r'\\'):
        return 'AF_PIPE'
    raise ValueError(f'Unrecognized address type: {addr!r}')


class Listener:
    """
    High-level listener for sockets or Named Pipes.
    """

    def __init__(
        self,
        address: Optional[Any] = None,
        family: Optional[str] = None,
        backlog: int = 1,
        authkey: Optional[bytes] = None
    ) -> None:
        self.family = family or (
            address and address_type(address)) or 'AF_INET'
        self.address = address or arbitrary_address(self.family)
        self.authkey = authkey

        if self.family == 'AF_PIPE':
            self._listener = PipeListener(self.address, backlog)
        else:
            sock = socket.socket(getattr(socket, self.family))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.address)  # type: ignore[arg-type]
            sock.listen(backlog)
            self._listener = sock

    def accept(self) -> mp_conn.Connection:
        """
        Accept a connection and perform optional HMAC authentication.
        """
        if self.family == 'AF_PIPE':
            conn = self._listener.accept()  # type: ignore[attr-defined]
        else:
            sock, _ = self._listener.accept()  # type: ignore[attr-defined]
            conn = mp_conn.Connection(sock.fileno())
            sock.close()
        if self.authkey:
            deliver_challenge(conn, self.authkey)
            answer_challenge(conn, self.authkey)
        return conn

    def close(self) -> None:
        """
        Close the listener socket or pipe.
        """
        try:
            self._listener.close()  # type: ignore[attr-defined]
        except Exception as e:
            logger.debug("Error closing listener: %s", e)


def Client(
    address: Any,
    family: Optional[str] = None,
    authkey: Optional[bytes] = None
) -> mp_conn.Connection:
    """
    Connect to a Listener and perform optional authentication.
    """
    fam = family or address_type(address)
    if fam == 'AF_PIPE':
        conn = PipeConnection(address)  # type: ignore[call-arg]
    else:
        with socket.create_connection(address) as sock:
            conn = mp_conn.Connection(sock.fileno())
    if authkey:
        answer_challenge(conn, authkey)
        deliver_challenge(conn, authkey)
    return conn


def Pipe(duplex: bool = True) -> Tuple[mp_conn.Connection, mp_conn.Connection]:
    """
    Return a pair of Connection objects connected by a pipe.
    """
    return mp_conn.Pipe(duplex)

# Authentication primitives


MESSAGE_LENGTH = 32


def deliver_challenge(conn: mp_conn.Connection, authkey: bytes) -> None:
    """
    Send a random challenge string and verify HMAC response.
    """
    assert isinstance(authkey, (bytes, bytearray))
    challenge = secrets.token_bytes(MESSAGE_LENGTH)
    # secure token source :contentReference[oaicite:5]{index=5}
    conn.send_bytes(challenge)
    expected = hmac.new(authkey, challenge, 'sha256').digest()
    response = conn.recv_bytes()
    if response != expected:
        raise AuthenticationError('Bad response')
    conn.send_bytes(b'WELCOME')


def answer_challenge(conn: mp_conn.Connection, authkey: bytes) -> None:
    """
    Receive challenge and respond with correct HMAC digest.
    """
    data = conn.recv_bytes()
    expected = hmac.new(authkey, data, 'sha256').digest()
    conn.send_bytes(expected)
    if conn.recv_bytes() != b'WELCOME':
        raise AuthenticationError('Authentication failed')

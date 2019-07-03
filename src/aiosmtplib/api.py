"""
Main public API.
"""
import ssl
from email.message import Message
from typing import Dict, Iterable, Optional, Tuple, Union, overload

from .compat import get_running_loop
from .connection import DEFAULT_TIMEOUT
from .response import SMTPResponse
from .smtp import SMTP


__all__ = ("send",)


@overload
async def send(
    message: Message,
    sender: Optional[str] = None,
    recipients: Optional[Union[str, Iterable[str]]] = None,
    hostname: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    mail_options: Optional[Iterable[str]] = None,
    rcpt_options: Optional[Iterable[str]] = None,
    timeout: Optional[float] = DEFAULT_TIMEOUT,
    source_address: Optional[str] = None,
    use_tls: bool = False,
    start_tls: bool = False,
    validate_certs: bool = True,
    client_cert: Optional[str] = None,
    client_key: Optional[str] = None,
    tls_context: Optional[ssl.SSLContext] = None,
    cert_bundle: Optional[str] = None,
) -> Tuple[Dict[str, SMTPResponse], str]:
    pass


@overload  # NOQA: F811
async def send(
    message: Union[str, bytes],
    sender: str = "",
    recipients: Union[str, Iterable[str]] = "",
    hostname: Optional[str] = None,
    port: Optional[int] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    mail_options: Optional[Iterable[str]] = None,
    rcpt_options: Optional[Iterable[str]] = None,
    timeout: Optional[float] = DEFAULT_TIMEOUT,
    source_address: Optional[str] = None,
    use_tls: bool = False,
    start_tls: bool = False,
    validate_certs: bool = True,
    client_cert: Optional[str] = None,
    client_key: Optional[str] = None,
    tls_context: Optional[ssl.SSLContext] = None,
    cert_bundle: Optional[str] = None,
) -> Tuple[Dict[str, SMTPResponse], str]:
    pass


async def send(  # NOQA: F811
    message,
    sender=None,
    recipients=None,
    username=None,
    password=None,
    start_tls=False,
    port=None,
    use_tls=False,
    **kwargs
):
    """
    Send an email message. On await, connects to the SMTP server using the details
    provided, sends the message, then disconnects.

    :param message:  Message text. Either an :py:class:`email.message.Message`
        object, ``str`` or ``bytes``. If an :py:class:`email.message.Message` object is
        provided, sender and recipients set in the message headers will be used, unless
        overridden by the respective keyword arguments.
    :keyword sender:  From email address. Not required if an
        :py:class:`email.message.Message` object is provided for the `message` argument.
    :keyword recipients: Recipient email addresses. Not required if an
        :py:class:`email.message.Message` object is provided for the `message` argument.
    :keyword hostname:  Server name (or IP) to connect to. Defaults to "localhost".
    :keyword port: Server port. Defaults ``465`` if ``use_tls`` is ``True``,
        ``587`` if ``start_tls`` is ``True``, or ``25`` otherwise.
    :keyword username:  Username to login as after connect.
    :keyword password:  Password for login after connect.
    :keyword source_address: The hostname of the client. Defaults to the
        result of :py:func:`socket.getfqdn`. Note that this call blocks.
    :keyword timeout: Default timeout value for the connection, in seconds.
        Defaults to 60.
    :keyword use_tls: If True, make the initial connection to the server
        over TLS/SSL. Note that if the server supports STARTTLS only, this
        should be False.
    :keyword start_tls: If True, make the initial connection to the server
        over plaintext, and then upgrade the connection to TLS/SSL. Not
        compatible with use_tls.
    :keyword validate_certs: Determines if server certificates are
        validated. Defaults to True.
    :keyword client_cert: Path to client side certificate, for TLS.
    :keyword client_key: Path to client side key, for TLS.
    :keyword tls_context: An existing :py:class:`ssl.SSLContext`, for TLS.
        Mutually exclusive with ``client_cert``/``client_key``.
    :keyword cert_bundle: Path to certificate bundle, for TLS verification.

    :raises ValueError: required arguments missing or mutually exclusive options
        provided
    """
    if not isinstance(message, Message):
        if not recipients:
            raise ValueError("Recipients must be provided with raw messages.")
        if not sender:
            raise ValueError("Sender must be provided with raw messages.")

    loop = get_running_loop()
    client = SMTP(
        loop=loop,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls,
        start_tls=start_tls,
        **kwargs
    )

    async with client:
        if isinstance(message, Message):
            result = await client.send_message(
                message, sender=sender, recipients=recipients
            )
        else:
            result = await client.sendmail(sender, recipients, message)

    return result

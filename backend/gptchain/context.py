import asyncio
import uuid
from contextvars import ContextVar
from typing import TYPE_CHECKING, Dict, Optional, Union

from gptchain.session import HTTPSession, WebsocketSession
from lazify import LazyProxy

if TYPE_CHECKING:
    from gptchain.client.cloud import AppUser, PersistedAppUser
    from gptchain.emitter import BasegptchainEmitter
    from gptchain.message import Message


class gptchainContextException(Exception):
    def __init__(self, msg="gptchain context not found", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class gptchainContext:
    loop: asyncio.AbstractEventLoop
    emitter: "BasegptchainEmitter"
    session: Union["HTTPSession", "WebsocketSession"]

    def __init__(self, session: Union["HTTPSession", "WebsocketSession"]):
        from gptchain.emitter import BasegptchainEmitter, gptchainEmitter

        self.loop = asyncio.get_running_loop()
        self.session = session
        if isinstance(self.session, HTTPSession):
            self.emitter = BasegptchainEmitter(self.session)
        elif isinstance(self.session, WebsocketSession):
            self.emitter = gptchainEmitter(self.session)


context_var: ContextVar[gptchainContext] = ContextVar("gptchain")


def init_ws_context(session_or_sid: Union[WebsocketSession, str]) -> gptchainContext:
    if not isinstance(session_or_sid, WebsocketSession):
        session = WebsocketSession.require(session_or_sid)
    else:
        session = session_or_sid
    context = gptchainContext(session)
    context_var.set(context)
    return context


def init_http_context(
    user: Optional[Union["AppUser", "PersistedAppUser"]] = None,
    auth_token: Optional[str] = None,
    user_env: Optional[Dict[str, str]] = None,
) -> gptchainContext:
    session = HTTPSession(
        id=str(uuid.uuid4()),
        token=auth_token,
        user=user,
        user_env=user_env,
    )
    context = gptchainContext(session)
    context_var.set(context)
    return context


def get_context() -> gptchainContext:
    try:
        return context_var.get()
    except LookupError:
        raise gptchainContextException()


context: gptchainContext = LazyProxy(get_context, enable_cache=False)

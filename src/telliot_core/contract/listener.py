import asyncio
import logging
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import Coroutine
from typing import List

import aiohttp
from web3._utils.method_formatters import log_entry_formatter
from web3.types import LogReceipt

logger = logging.getLogger("__name__")

AsyncCallable = Callable[[Any], Coroutine[Any, Any, None]]


async def event_message_handler(msg: Any) -> None:
    log_receipt: LogReceipt = log_entry_formatter(msg)
    logger.info(f"handled event message: {log_receipt}")


async def subscribe_contract_events(
    ws: aiohttp.ClientWebSocketResponse, contract_address: str
) -> None:
    logger.info(f"Subscribing to contract events at address {contract_address}")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_subscribe",
        "params": ["logs", {"address": contract_address}],
    }

    await ws.send_json(request)

    subscription_response = await ws.receive_json()
    _ = subscription_response.get("id")
    sub_result = subscription_response.get("result")
    logger.info(
        f"Subscription complete: result={sub_result} for address {contract_address}"
    )


async def subscribe_blocks(ws: aiohttp.ClientWebSocketResponse) -> None:
    logger.info("Subscribing to newHeads")

    msg = {"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}

    await ws.send_json(msg)

    subscription_response = await ws.receive_json()
    _ = subscription_response.get("id")
    sub_result = subscription_response.get("result")

    logger.info(f"newHead subscription complete: result={sub_result}")


async def receive_messages(
    ws: aiohttp.ClientWebSocketResponse, handler: AsyncCallable
) -> None:
    while True:
        try:
            message = await asyncio.wait_for(ws.receive_json(), timeout=60)
            await handler(message)
        except asyncio.CancelledError:
            logger.debug("Listener cancelled")
            raise
        except asyncio.exceptions.TimeoutError:
            logger.debug("Listener Timed out, restarting.")
            continue


async def block_listener(session: aiohttp.ClientSession, ws_url: str) -> None:
    async def block_message_handler(msg: Any) -> None:
        sub_id = msg["params"]["subscription"]
        logger.info(f"handled block subscription: {sub_id}")

    async with session.ws_connect(ws_url) as ws2:
        await subscribe_blocks(ws2)
        await receive_messages(ws2, block_message_handler)


async def contract_event_listener(
    session: aiohttp.ClientSession,
    ws_url: str,
    address: str,
    message_handler: AsyncCallable,
) -> None:

    async with session.ws_connect(ws_url) as ws1:
        await subscribe_contract_events(ws1, address)
        await receive_messages(ws1, message_handler)


@dataclass
class AddressEventListener:
    """A listener that handles all event logs from a contract address"""

    #: Contract address
    address: str

    #: Handler that takes the received JSON message a single argument
    handler: AsyncCallable


async def listener_client(
    ws_url: str, chain_id: int, listeners: List[AddressEventListener]
) -> None:
    async with aiohttp.ClientSession() as session:
        logger.info("Listener session created")

        tasks = [block_listener(session, ws_url)]
        for listener in listeners:
            tasks.append(
                contract_event_listener(
                    session, ws_url, listener.address, listener.handler
                )
            )

        await asyncio.gather(*tasks)

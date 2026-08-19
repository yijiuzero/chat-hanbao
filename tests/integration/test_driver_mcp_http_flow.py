# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from hanbao.drivers.capabilities import DriverInvocation
from hanbao.drivers.contracts import CredentialRef, DriverCard, PolicyRule
from hanbao.drivers.credentials.store import AsyncCredentialStore
from hanbao.drivers.credentials.types import CredentialRecord
from hanbao.drivers.handlers.mcp import MCPDriverHandler
from hanbao.drivers.manager import DriverManager
from hanbao.drivers.storage import card_path, dump_card
from tests.integration.driver_mcp_fakes import (
    FakeHttpClient,
    patch_mcp_runtime_clients,
)


@pytest.mark.asyncio
async def test_driver_mcp_http_header_secret_flow(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_mcp_runtime_clients(monkeypatch)
    store = AsyncCredentialStore(tmp_path / "credentials.yaml")
    await store.put(
        CredentialRecord(
            ref="mcp/http_echo",
            kind="static",
            secrets={"authorization": "Bearer static-token"},
        ),
    )
    dump_card(
        DriverCard(
            name="http_echo",
            protocol="mcp",
            endpoint={
                "transport": "streamable_http",
                "url": "http://127.0.0.1:18080/mcp",
                "headers": {
                    "public": {"X-Client-Name": "hanbao-test"},
                    "secret_refs": {"Authorization": "authorization"},
                },
            },
            credentials={
                "default": CredentialRef("static", "mcp/http_echo"),
            },
            policy=[PolicyRule(subject="*", effect="allow")],
        ),
        card_path(tmp_path / "drivers", "http_echo", protocol="mcp"),
    )
    manager = DriverManager(tmp_path / "drivers", store)
    manager.register_handler_type("mcp", MCPDriverHandler)

    await manager.build_drivers()
    capability = next(
        item
        for item in await manager.list_capabilities(kind="tool")
        if item.name == "inspect_headers"
    )
    result = await manager.invoke_capability(
        DriverInvocation(capability.capability_id, {}),
    )

    assert result.ok is True
    assert result.value["headers"]["Authorization"] == "Bearer static-token"
    assert result.value["headers"]["X-Client-Name"] == "hanbao-test"
    assert (
        FakeHttpClient.instances[0].kwargs["headers"]
        == result.value["headers"]
    )

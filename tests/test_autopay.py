import pytest
from brownie import accounts
from brownie import AutopayMock

from telliot_core.apps.core import TelliotCore
from telliot_core.fetch.fetchflex.autopay import FetchFlexAutopayContract


@pytest.fixture(scope="module")
def mock_autopay_contract():
    return accounts[0].deploy(AutopayMock)

@pytest.mark.skip(reason="no way of currently testing external chain dependent tests")
@pytest.mark.asyncio
async def test_get_current_tip(mumbai_test_cfg, mock_autopay_contract):
    async with TelliotCore(config=mumbai_test_cfg) as core:
        account = core.get_account()

        autopay = FetchFlexAutopayContract(core.endpoint, account)
        autopay.address = mock_autopay_contract.address
        autopay.connect()

        query_id = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000002")

        result, status = await autopay.get_current_tip(query_id=query_id)
        assert status.ok
        assert result == len(query_id)

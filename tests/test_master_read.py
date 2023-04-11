import pytest
from brownie import accounts
from brownie import FetchXMasterMock

from telliot_core.apps.core import TelliotCore
from telliot_core.fetch.fetchx.master import account_status_map
from telliot_core.fetch.fetchx.master import FetchxMasterContract
from telliot_core.utils.timestamp import TimeStamp


@pytest.fixture
def fetchx_master_mock_contract():
    """Mock the FetchXMaster contract"""
    return accounts[0].deploy(FetchXMasterMock)

@pytest.mark.skip(reason="no way of currently testing external chain dependent tests")
@pytest.mark.asyncio
async def test_get_staker_info(rinkeby_test_cfg, fetchx_master_mock_contract):
    """Test the FetchXMaster contract"""

    async with TelliotCore(config=rinkeby_test_cfg) as core:
        account = core.get_account()
        fetchx = FetchxMasterContract(core.endpoint, account)
        fetchx.address = fetchx_master_mock_contract.address
        fetchx.connect()

        result, status = await fetchx.getStakerInfo(fetchx.address)

        assert status.ok
        assert len(result) == 2
        assert result[0] in account_status_map.values()
        assert isinstance(result[1], TimeStamp)

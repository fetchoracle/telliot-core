"""Pytest Fixtures used for testing Pytelliot"""
import os
import secrets

import pytest
from brownie import accounts
from chained_accounts import ChainedAccount
from chained_accounts import find_accounts

from telliot_core.apps.telliot_config import TelliotConfig


@pytest.fixture(scope="session", autouse=True)
def local_cfg():
    """Use local Ganache endpoint as web3 provider."""
    cfg = TelliotConfig()

    # Use Polygon mumbai testnet chain id, since this will trigger TelliotConfig
    # to use TellorFlex contracts.
    cfg.main.chain_id = 80001

    # Override endpoint with localhost and default Ganache port
    default_endpoint = cfg.get_endpoint()
    default_endpoint.url = "http://127.0.0.1:8545"

    # Create fake test account
    pk = secrets.token_hex(32)
    accounts.add(pk)
    chained_accts = find_accounts(name="_test_account")
    # print(dir(ChainedAccount))
    if not chained_accts or chained_accts[0].address != "0x3d79f9a83c8bfc5887741a771609da1ac3101f5a":
        ChainedAccount.add("_test_account", chains=80001, key=pk, password="")

    # Verify correct test account used
    # test_acct = find_accounts(name="_test_account")[0]
    # assert to_checksum_address(test_acct.address) == accounts[-1].address

    # endpoint = cfg.get_endpoint()
    # print("url:", endpoint.url)
    # chain.mine(10)
    # block = endpoint._web3.eth.get_block("latest")
    # assert block.number == 10

    return cfg


@pytest.fixture(scope="session", autouse=True)
def rinkeby_cfg():
    """Get rinkeby endpoint from config

    If environment variables are defined, they will override the values in config files
    """
    cfg = TelliotConfig()

    # Override configuration for rinkeby testnet
    cfg.main.chain_id = 4

    rinkeby_endpoint = cfg.get_endpoint()
    # assert rinkeby_endpoint.network == "rinkeby"

    if os.getenv("NODE_URL", None):
        rinkeby_endpoint.url = os.environ["NODE_URL"]

    rinkeby_accounts = find_accounts(chain_id=4)
    if not rinkeby_accounts:
        # Create a test account using PRIVATE_KEY defined on github.
        key = os.getenv("PRIVATE_KEY", None)
        if key:
            ChainedAccount.add("git-rinkeby-key", chains=4, key=os.environ["PRIVATE_KEY"], password="")
        else:
            raise Exception("Need a rinkeby account")

    return cfg


@pytest.fixture(scope="session", autouse=True)
def mumbai_cfg():
    """Return a test telliot configuration for use on polygon-mumbai

    If environment variables are defined, they will override the values in config files
    """
    cfg = TelliotConfig()

    # Override configuration for mumbai testnet
    cfg.main.chain_id = 80001

    endpt = cfg.get_endpoint()
    if "INFURA_API_KEY" in endpt.url:
        endpt.url = f'https://polygon-mumbai.infura.io/v3/{os.environ["INFURA_API_KEY"]}'

    mumbai_accounts = find_accounts(chain_id=80001)
    if not mumbai_accounts:
        # Create a test account using PRIVATE_KEY defined on github.
        key = os.getenv("PRIVATE_KEY", None)
        if key:
            ChainedAccount.add("git-mumbai-key", chains=80001, key=os.environ["PRIVATE_KEY"], password="")
        else:
            raise Exception("Need a mumbai account")

    return cfg


@pytest.fixture(scope="session", autouse=True)
def ropsten_cfg():
    """Return a test telliot configuration for use on polygon-mumbai

    If environment variables are defined, they will override the values in config files
    """
    cfg = TelliotConfig()

    # Override configuration for ropsten testnet
    cfg.main.chain_id = 3

    endpt = cfg.get_endpoint()
    if "INFURA_API_KEY" in endpt.url:
        endpt.url = f'wss://ropsten.infura.io/ws/v3/{os.environ["INFURA_API_KEY"]}'

    accounts = find_accounts(chain_id=3)
    if not accounts:
        # Create a test account using PRIVATE_KEY defined on github.
        key = os.getenv("PRIVATE_KEY", None)
        if key:
            ChainedAccount.add("git-ropsten-key", chains=3, key=os.environ["PRIVATE_KEY"], password="")
        else:
            raise Exception("Need a ropsten account")

    return cfg


@pytest.fixture(scope="session", autouse=True)
def fuse_cfg():
    """Return a test telliot configuration for use on polygon-mumbai

    If environment variables are defined, they will override the values in config files
    """
    cfg = TelliotConfig()

    # Override configuration for fuse testnet
    cfg.main.chain_id = 122

    accounts = find_accounts(chain_id=122)
    if not accounts:
        # Create a test account using PRIVATE_KEY defined on github.
        key = os.getenv("PRIVATE_KEY", None)
        if key:
            ChainedAccount.add("git-fuse-key", chains=122, key=os.environ["PRIVATE_KEY"], password="")
        else:
            raise Exception("Need a Fuse account")

    return cfg

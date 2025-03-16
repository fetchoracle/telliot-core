import getpass
import os

from chained_accounts import ChainedAccount
from hexbytes import HexBytes


def ask_for_password(name: str) -> str:
    password1 = getpass.getpass(f"Enter encryption password for {name}: ")
    password2 = getpass.getpass("Confirm password: ")
    if password2 != password1:
        raise Exception(f"Passwords do not match: {name}")
    password = password1

    return password


def lazy_unlock_account(account: ChainedAccount) -> None:
    if account.is_unlocked:
        return
    else:
        # Try unlocking with empty password
        try:
            account.unlock("")
            return
        except ValueError:

            if os.getenv("PASSWORD"):
                try:
                    os.getenv("PASSWORD")
                    print(f'PASSWORD .env set. Using it to {account.name} unlock.')
                    account.unlock(str(os.getenv("PASSWORD")))
                    print(f'Acc {account.name} unlocked with .env PASSWORD')
                    return
                except ValueError:
                    print("Password from .env unlock failed.")
            try:
                print('Need manual input to unlock account')
                password = getpass.getpass(f"Enter encryption password for {account.name}: ")
                account.unlock(password)
                return
            except ValueError:
                raise Exception(f"Invalid password for {account.name}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise


def lazy_key_getter(account: ChainedAccount) -> HexBytes:

    lazy_unlock_account(account)

    return account.key  # type: ignore

import enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import Literal


from pydantic import BaseModel
from pydantic import validator
from telliot.response_type import ResponseType
from web3 import Web3


@enum.unique
class PriceType(str, enum.Enum):
    """Enumeration of supported price types"""

    current = "current"
    eod = "end of day"
    twap_custom = "custom time-weighted average"
    twap_1hr = "1 hour time-weighted average"
    twap_24hr = "24 hour time-weighted average"


CoerceToRequestId = Union[bytearray, bytes, int, str]


def to_request_id(value: CoerceToRequestId) -> bytes:
    """Coerce input type to request_id in Bytes32 format

    Args:
        value:  CoerceToRequestId

    Returns:
        bytes: Request ID
    """
    if isinstance(value, bytearray):
        value = bytes(value)

    if isinstance(value, bytes):
        bytes_value = value

    elif isinstance(value, str):
        value = value.lower()
        if value.startswith("0x"):
            value = value[2:]
        bytes_value = bytes.fromhex(value)

    elif isinstance(value, int):
        bytes_value = value.to_bytes(32, "big", signed=False)

    else:
        raise TypeError("Cannot convert {} to request_id".format(value))

    if len(bytes_value) != 32:
        raise ValueError("Request ID must have 32 bytes")

    return bytes_value


class OracleQuery(BaseModel):
    """Base class for all tellorX queries"""

    #: Type field is required to support registry export/import through json
    #: Must be overridden in all OracleQuery subclasses
    type: Literal['OracleQuery']='OracleQuery'

    #: Unique query name (Tellor Assigned)
    uid: str

    #: Descriptive name
    name: str

    #: Data Specification
    data: Optional[bytes]

    #: Response specification
    response_type: ResponseType

    #: Integer Request ID (Legacy requests only)
    legacy_request_id: Optional[int]

    #: True if this is a legacy price query
    is_legacy = property(lambda self: self.legacy_request_id is not None)

    #: Container to register subclasses for pydantic export hack (see below)
    _types: Dict[str, type] = {}

    @property
    def request_id(self) -> bytes:
        """Return the modern or legacy request ID

        Returns:
            bytes: 32-byte Request ID
        """
        if self.legacy_request_id is not None:
            return self.legacy_request_id.to_bytes(32, "big", signed=False)
        else:
            return bytes(Web3.keccak(self.data))

    @validator("legacy_request_id")
    def must_be_less_than_100(cls, v):  # type: ignore
        if v is not None:
            if v > 100:
                raise ValueError("Legacy request ID must be less than 100")
        return v

    # --------------------------------------------------------------
    # The following machinery is used to force Pydantic to properly
    # serialize and deserialize OracleQuery subclasses by including
    # type info in the JSON stream
    # Per https://github.com/samuelcolvin/pydantic/issues/2177
    # --------------------------------------------------------------

    # used to register automatically all the submodels in `_types`.
    def __init_subclass__(cls, type: Optional[str] = None):
        cls._types[type or cls.__name__.lower()] = cls

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: Dict[str, Any]) -> 'OracleQuery':
        try:
            query_cls = value.pop('type')
            # init with right Pet submodel
            return cls._types[query_cls](**value)
        except:
            raise ValueError('...')



class PriceQuery(OracleQuery):
    """A query requesting the price of an asset in a specified currency."""

    #: Type field is required to support registry export/import through json
    #: Must be overridden in all OracleQuery subclasses
    type: Literal['PriceQuery']='PriceQuery'

    #: Asset symbol
    asset: str = ""

    #: Price currency symbol
    currency: str = ""

    #: Price Type
    price_type: PriceType

    class Config:
        # Export price_type as string
        use_enum_values = True

    def __init__(self, **kwargs: Any):
        if "response_type" not in kwargs:
            kwargs["response_type"] = ResponseType(abi_type="ufixed256x6", packed=False)

        super().__init__(**kwargs)


class QueryRegistry(BaseModel):
    """A class for constructing the official query registry"""

    #: Dict of registered queries keyed by uid
    #: Todo: make private/read-only
    queries: Dict[str, OracleQuery]

    def register(self, q: OracleQuery) -> None:
        """Add a query to the registry"""

        # Make sure uid is unique in registry
        unique_ids = self.get_uids()
        if q.uid in unique_ids:
            raise ValueError(
                "Cannot add query to registry: UID {} already used".format(q.uid)
            )

        # Assign to registry
        self.queries[q.uid] = q

    def get_query_by_request_id(
        self, request_id: CoerceToRequestId
    ) -> Optional[OracleQuery]:
        """Return Query corresponding to request_id"""

        request_id_coerced = to_request_id(request_id)

        for query in self.queries.values():
            if query.request_id == request_id_coerced:
                return query

        return None

    def get_request_ids(self) -> List[bytes]:
        """Return a list of registered Request IDs."""
        return [q.request_id for q in self.queries.values()]

    def get_uids(self) -> List[str]:
        """Return a list of registered UIDs."""
        return [q.uid for q in self.queries.values()]

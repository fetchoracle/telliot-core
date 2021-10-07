from web3 import Web3

from telliot.queries.query import OracleQuery
from telliot.response_type import ResponseType
from pydantic import Field


class StaticQuery(OracleQuery):
    """ Static Oracle Query

    A static uses a fixed value for tip data.
    The request_id is also fixed according the keccak algorithm
    """

    type: str = Field('StaticQuery', constant=True)

    #: Question
    static_question: str

    #: Response specification: defines required data type of
    #: `value` in `TellorX.submitValue` function call
    static_response_type: ResponseType

    @property
    def response_type(self) -> ResponseType:
        """ Concrete implementation  """
        return self.static_response_type

    @property
    def request_id(self) -> bytes:
        """Return the modern or legacy request ID

        Returns:
            bytes: 32-byte Request ID
        """
        return bytes(Web3.keccak(self.tip_data))

    @property
    def question(self) -> str:
        return self.static_question

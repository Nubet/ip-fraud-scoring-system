from app.adapters.maxmind.asn_reader import MaxMindASNReader


class _FakeASNResponse:
    def __init__(self, org: str):
        self.autonomous_system_organization = org


class _FakeReader:
    def __init__(self, org: str):
        self.org = org

    def asn(self, ip: str):
        return _FakeASNResponse(self.org)


async def test_reader_returns_false_without_db_path() -> None:
    reader = MaxMindASNReader(db_path=None)
    assert await reader.is_data_center("8.8.8.8") is False


async def test_reader_returns_false_for_invalid_ip() -> None:
    reader = MaxMindASNReader(db_path=None)
    reader._reader = _FakeReader("Amazon Technologies")
    assert await reader.is_data_center("not-an-ip") is False


async def test_reader_detects_data_center() -> None:
    reader = MaxMindASNReader(db_path=None)
    reader._reader = _FakeReader("Amazon Technologies")
    assert await reader.is_data_center("8.8.8.8") is True


async def test_reader_returns_false_for_residential_org() -> None:
    reader = MaxMindASNReader(db_path=None)
    reader._reader = _FakeReader("Example Residential ISP")
    assert await reader.is_data_center("8.8.8.8") is False

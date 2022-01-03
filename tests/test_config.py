from io import StringIO

import pytest

from gnucash_asset_allocation.config import Config, InvalidConfigException


@pytest.fixture(name="valid_config")
def valid_config_fixture(mocker):
    fake_file = StringIO(
        """[gnucash]
file = path/to/file/example.gnucash
file_format = xml
account = Assets:Investments:Brokerage Account

[allocation]
ZAG.TO = 20
XIC.TO = 24
VUN.TO = 24
AVUV = 8.0
XEF.TO = 12.8
AVDV = 4.8
XEC.TO = 6.4"""
    )

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", return_value=fake_file)

    config = Config()

    return config


def test_config_file(valid_config):
    assert valid_config.file == "path/to/file/example.gnucash"


def test_config_acount(valid_config):
    assert valid_config.account == "Assets:Investments:Brokerage Account"


def test_config_allocation(valid_config):
    assert valid_config.allocation == {
        "ZAG.TO": 20,
        "XIC.TO": 24,
        "VUN.TO": 24,
        "AVUV": 8.0,
        "XEF.TO": 12.8,
        "AVDV": 4.8,
        "XEC.TO": 6.4,
    }


def test_config_file_does_not_exist(mocker):
    mocker.patch("os.path.exists", return_value=False)

    with pytest.raises(InvalidConfigException):
        Config()


@pytest.mark.parametrize(
    "fake_file",
    [
        """[gnucash]
account = Assets:Investments:Brokerage Account

[allocation]
ZAG.TO = 20
XIC.TO = 24
VUN.TO = 24
AVUV = 8.0
XEF.TO = 12.8
AVDV = 4.8
XEC.TO = 6.4""",
        """[gnucash]
file = path/to/file/example.gnucash

[allocation]
ZAG.TO = 20
XIC.TO = 24
VUN.TO = 24
AVUV = 8.0
XEF.TO = 12.8
AVDV = 4.8
XEC.TO = 6.4""",
        """[gnucash]
file = path/to/file/example.gnucash
base_currency = CAD
""",
        """[allocation]
ZAG.TO = 20
XIC.TO = 24
VUN.TO = 24
AVUV = 8.0
XEF.TO = 12.8
AVDV = 4.8
XEC.TO = 6.4""",
    ],
)
def test_missing_data(mocker, fake_file):
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", return_value=StringIO(fake_file))

    with pytest.raises(InvalidConfigException):
        Config()


def test_allocation_sum_not_100(mocker):
    fake_file = StringIO(
        """[gnucash]
file = path/to/file/example.gnucash
account = Assets:Investments:Brokerage Account

[allocation]
ZAG.TO = 20
XIC.TO = 24
VUN.TO = 24
AVUV = 8.0
XEF.TO = 12.9
AVDV = 4.8
XEC.TO = 6.4"""
    )

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", return_value=fake_file)

    with pytest.raises(InvalidConfigException):
        Config()

'''
seleniumでのセッションを開始する関数群
'''

from selenium.webdriver import Remote, ChromeOptions, FirefoxOptions, EdgeOptions
from typing import Union


def create_driver(options: Union[ChromeOptions, FirefoxOptions, EdgeOptions]) -> Remote:
    """hubに接続したwebdriverを返す
    Args:
        options: ([browsername]Options) webdriver option
    Returns:
        (Remote) webdriver
    """
    driver = Remote(
        # docker-compose.dev.ymlの
        # selenium/hubイメージのサービス名で繋ぐこと
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    return driver


def get_browser_option(browser_name: str) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions]:
    """指定したブラウザのオプションを返す,
    存在しないブラウザが入力された時はchromeのオプションを返す
    Args:
        browser_name: browser name
    Returns:
        ([browsername]Options) webdriver options
    Notes:
        browser_nameはfirefox, edge, chromeのいずれかであること
    """
    if browser_name == "firefox":
        options = FirefoxOptions()
    elif browser_name == "edge":
        options = EdgeOptions()
    elif browser_name == "chrome":
        options = ChromeOptions()
    else:
        print("[create_webdiver] error: Specified browser is not supported")
        options = ChromeOptions()
    return options


def set_browser_version(options: Union[ChromeOptions, FirefoxOptions, EdgeOptions], browser_version: int) -> Union[ChromeOptions, FirefoxOptions, EdgeOptions]:
    """webdriver.Optionにバージョン情報を追加する
    Args:
        options: ([browsername]Options) webdriver option
        browser_version: browser version
    Returns:
        ([browsername]Options) webdriver option
    Notes:
        browser_versionに入力する数値は正の整数であること
    """
    str_ver = browser_version
    if type(str_ver) is int:
        str_ver = str(str_ver) + ".0"
    else:
        str_ver = str_ver + ".0"
    options.set_capability("browserVersion", str_ver)
    return options


def create_driver_connected_hub(browser_name: str, browser_version: int) -> Remote:
    """指定したブラウザでselenium-hubに接続した状態のwebドライバーを返す
    Args:
        browser_name: browser name
        version: browser version
    Returns:
        (Remote) webdriver
    Notes:
        browser_nameはfirefox, edge, chromeのいずれかであること,
        browser_versionに入力する数値は正の整数であること
    """
    options = get_browser_option(browser_name)
    options = set_browser_version(options, browser_version)
    driver = create_driver(options)
    return driver

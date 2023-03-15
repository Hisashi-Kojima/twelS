'''
seleniumでのセッションを開始する関数群
'''

from selenium import webdriver
from typing import Union


def create_driver(options: Union[webdriver.ChromeOptions, webdriver.FirefoxOptions, webdriver.EdgeOptions]) -> webdriver.Remote:
    """hubに接続したwebdriverを返す
    Args:
        options: (webdriver.[browsername]Options) webdriver option
    Return:
        (webdriver.Remote) webdriver
    """
    driver = webdriver.Remote(
        # サービスのコンテナ名で繋ぐこと
        command_executor='http://selenium-hub:4444/wd/hub',
        options=options,
    )
    return driver

def get_browser_option(browser: str) -> Union[webdriver.ChromeOptions, webdriver.FirefoxOptions, webdriver.EdgeOptions]:
    """指定したブラウザのオプションを返す
    存在しないブラウザが入力された時はchromeのオプションになる
    Args:
        browser: (string) browser name
    Return:
        (webdriver.[browsername]Options) webdriver options
    Note: 
        対応しているブラウザはfirefox, edge, chrome
    """
    
    if browser == "firefox" :
        options = webdriver.FirefoxOptions()
    elif browser == "edge" :
        options = webdriver.EdgeOptions()
    elif browser == "chrome" :
        options = webdriver.ChromeOptions()
    else:
        print("[create_webdiver] error: Specified browser is not supported")
        options = webdriver.ChromeOptions()
    return options

def set_browser_version(options: Union[webdriver.ChromeOptions, webdriver.FirefoxOptions, webdriver.EdgeOptions], version: int) -> Union[webdriver.ChromeOptions, webdriver.FirefoxOptions, webdriver.EdgeOptions]:
    """webdriver.Optionにバージョン情報を追加する
    Args:
        options (webdriver.[browsername]Options) webdriver option
        version (int) browser version
    Return:
        (webdriver.[browsername]Options) webdriver option
    Note:
        versionに入力する数値は正の整数であること
    """
    str_ver = version
    if type(str_ver) is int:
        str_ver = str(str_ver) + ".0"
    else:
        str_ver = str_ver + ".0"
    options.set_capability("browserVersion", str_ver)
    return options

def create_driver_connected_hub(browser_name: str, version: int) -> webdriver.Remote:
    """指定したブラウザでselenium-hubに接続した状態のwebドライバーを返す
    Args:
        browser_name (string) browser name
        version (int) browser version
    Return:
        (webdriver.Remote) webdriver
    Note:
        versionに入力する数値は正の整数であること, 
        browser_nameはfirefox, edge, chromeのいずれかであること
    """
    options = get_browser_option(browser_name)
    options = set_browser_version(options, version)
    driver = create_driver(options)
    return driver

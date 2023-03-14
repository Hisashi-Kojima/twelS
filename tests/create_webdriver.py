'''
seleniumでのセッションを開始する関数群
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from typing import Tuple, Union


def Create_Driver(options: Options) -> webdriver:
    """hubに接続したwebdriverを返す
    Args:
        options: (Options) webdriver option
    Return:
        (webdriver) webdriver
    """
    driver = webdriver.Remote(
        command_executor=f'http://selenium-hub:4444/wd/hub',
        options=options,
    )
    return driver

def Get_BrowserOption(browser: str) -> webdriver.ChromeOptions:
    """指定したブラウザのオプションを返す
    存在しないブラウザが入力された時はchromeのオプションになる
    Args:
        browser: (string) browser name
    Return:
        (Options) webdriver options
    """
    
    if browser == "firefox" :
        options = webdriver.FirefoxOptions()
    elif browser == "edge" :
        options = webdriver.EdgeOptions()
    elif browser == "safari" :
        options = webdriver.SafariOptions()
    elif browser == "chrome" :
        options = webdriver.ChromeOptions()
    else:
        print("[create_webdiver] error: Specified browser is not supported")
        options = webdriver.ChromeOptions()
    return options

def Set_Browser_Version(options, version):
    """webdriver.Optionにバージョン情報を追加する
    Args:
        options (webdriver.Option) webdriver option
        version (int, string) browser version
    Return:
        (webdriver) webdriver
    Note:
        versionに入力する数値(文字列)は正の整数であること
    """
    str_ver = version
    if type(str_ver) is int:
        str_ver = str(str_ver) + ".0"
    else:
        str_ver = str_ver + ".0"
    options.set_capability("browserVersion", str_ver)
    return options

def Create_Driver_ConnectedHub(browser_name: str, version: int) -> webdriver:
    """指定したブラウザでhubにのみ接続した状態のドライバーを返す
    Args:
        browser_name (string) browser name
        version (int, string) browser version
    Return:
        (webdriver) webdriver
    Note:
        versionに入力する数値(文字列)は正の整数であること
    """
    options = Get_BrowserOption(browser_name)
    options = Set_Browser_Version(options, version)
    driver = Create_Driver(options)
    return driver

print(type(Get_BrowserOption("chrome")))
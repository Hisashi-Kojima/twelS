'''
seleniumでのセッションを開始する関数群
'''

from selenium import webdriver

def Create_Driver(options):
    '''
    hubに接続したwebdriverを返す
    options: (object) webdriver option
    return: (object) webdriver
    '''
    # with asで開くことで終了時に自動で閉じる
    with webdriver.Remote(
        command_executor=f'http://selenium-hub:4444/wd/hub',
        options=options,
    ) as driver:
        return driver

def Get_BrowserOption(browser):
    '''
    指定したブラウザのオプションを返す
    存在しないブラウザの時はchromeのオプションになる
    browser: (string)
    return: (object) browser driver options
    '''
    if browser == "firefox" :
        # firefox
        options = webdriver.FirefoxOptions()
    elif browser == "edge" :
        # edge
        options = webdriver.EdgeOptions()
    elif browser == "safari" :
        # safari
        options = webdriver.SafariOptions()
    elif browser == "chrome" :
        # chrome
        options = webdriver.ChromeOptions()
    else:
        print("[create_webdiver] error: Specified browser is not supported")
        options = webdriver.ChromeOptions()
    return options

def Set_Browser_Version(options, version):
    '''
    optionsにバージョン情報を追加する
    注意: バージョンは110のように入力すること
    options: (object) webdriver option
    version: (string or int) browser version
    return: (object) webdriver option
    '''
    str_ver = version
    if type(str_ver) is int:
        str_ver = str(str_ver) + ".0"
    else:
        str_ver = str_ver + ".0"
    options.set_capability("browserVersion", str_ver)
    return options

def GET_TwelS(driver):
    '''
    TwelSのテストサーバ(コンテナ)にGETを飛ばす
    driver: (object) webdriver
    return: (object) webdriver
    '''
    try:
        driver.get('http://python:8000/')
    except Exception as e:
        print(e)
    return driver

def Create_Conected_Driver(browser_name, version):
    '''
    指定したブラウザでTwelSのテストサーバ(コンテナ)に接続した
    状態のドライバーを返す
    <注意> versionは正の整数を入力すること
    例: Create_Conected_Driver("chrome", 110)
    browser_name: (string) browser name
    version: (int or string) browser version
    return: (object) webdriver
    '''
    options = Get_BrowserOption(browser_name)
    options = Set_Browser_Version(options, version)
    driver = Create_Driver(options)
    driver = GET_TwelS(driver)
    return driver

def Create_UnConected_Driver(browser_name, version):
    '''
    指定したブラウザでhubにのみ接続した状態のドライバーを返す
    <注意> versionは正の整数を入力すること
    例: Create_Conected_Driver("chrome", 110)
    browser_name: (string) browser name
    version: (int or string) browser version
    return: (object) webdriver
    '''
    options = Get_BrowserOption(browser_name)
    options = Set_Browser_Version(options, version)
    driver = Create_Driver(options)
    return driver


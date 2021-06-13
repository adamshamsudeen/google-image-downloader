from selenium.webdriver.chrome.options import Options
def get_options():
    
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/80.0.3987.132 Safari/537.36'
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--allow-cross-origin-auth-prompt")
    # options.add_argument("--start-fullscreen")
    options.add_argument("--window-size=1920x1080")
  
    return options
    new_driver = webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=options)
    # new_driver = webdriver.Firefox(executable_path = DRIVER_BIN_FIRE)
    new_driver.get(f"https://www.google.com/search?q={'+'.join(SEARCH_TERMS)}&source=lnms&tbm=isch&sa=X")
    return new_driver
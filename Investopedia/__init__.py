"""
    Investopedia API
    Made by Monnapse
"""

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.chrome.service import Service # FOR SPECIFIED DIRECTORY
import time
from enum import Enum

wait_time = 5

# DRIVER
options = Options() 
#options.headless = True
#options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument('window-size=1920x1080')
options.add_experimental_option("detach", True)

#service = Service(executable_path="/lib/chromium-browser/chromedriver") # FOR SPECIFIED DIRECTORY, THIS DIRECTORY IS FOR RASPBERRY PI

#driver = webdriver.Chrome(options=options, service=service)  # FOR SPECIFIED DIRECTORY
driver = webdriver.Chrome(options=options) 
driver.set_window_size(1920, 1080)
web_driver_waiter = WebDriverWait(driver, wait_time)

class Duration(Enum):
    day_only = 1
    good_until_cancel = 2

class OrderType(Enum):
    limit = 1
    market = 2
    stop_limit = 3

class Action(Enum):
    buy = 1
    sell = 2

class PortfolioStock:
    symbol = None
    description = None
    current_price = None
    day_change_dollor = None
    day_change_percent = None
    purchase_price = None
    quantity = None
    total_value = None
    total_change_dollar = None
    total_change_percent = None

class Account:
    def __init__(self, username: str, password:str):
        """
            Logs into Investopedia Account
        """

        self.base_url = "https://www.investopedia.com"
        self.portfolio_url = "/simulator/portfolio"

        self.new_page(self.portfolio_url)

        # Sign in
        username_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'username')))#driver.find_element(By.ID, "username")
        username_element.send_keys(username)

        password_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'password')))#driver.find_element(By.ID, "password")
        password_element.send_keys(password)

        login_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'login')))#driver.find_element(By.ID, "login")
        login_element.click()

        time.sleep(1)
        try:
            if driver.find_element(By.CLASS_NAME, "alert-error"):
                # Restart
                print("Could not login now restarting")
                self.__init__(username, password)
        except:
            pass
        print("Succesfully logged in")

    def new_page(self, url: str):
        if driver.current_url != self.base_url + url:
            driver.get(self.base_url + url)
            print("Loaded New page")
        else:
            print("Page already loaded")

        time.sleep(0.25) # Wait for page to be loaded

    def get_account_overview(self):
        """
            Gets Accounts Value, Buying Power, and Cash
        """
        try:
        
            self.new_page(self.portfolio_url)

            return {
                "account_value": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="account-value-text"]'))).text, #driver.find_element(By.CSS_SELECTOR, 'div[data-cy="account-value-text"]').text,
                "buying_power": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="buying-power-text"]'))).text,#driver.find_element(By.CSS_SELECTOR, 'div[data-cy="buying-power-text"]').text,
                "cash": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="cash-text"]'))).text#driver.find_element(By.CSS_SELECTOR, 'div[data-cy="cash-text"]').text
            }
        except:
            pass
    
    def change_game_session(self, session_name: str):
        try:
            #data-cy="portfolio-select"
            #self.new_page("/simulator/trade/stocks")
            web_driver_waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="portfolio-select"]'))).click()
            #/html/body/div[1]/div/div/div[2]/main/div/div[1]/div/div[1]/div[2]/div/div/div/div
            list = web_driver_waiter.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[1]/div/div[1]/div[2]/div/div/div/div')))
            try:
                session = list.find_element(By.XPATH, f"//*[contains(text(), '{session_name}')]")
                session.click()
            except:
                pass
            print("Successfuly change game session to " + session_name)
        except:
            pass

    def click_on_element_BY(self, by: str = By.ID, value: str = None):
        """
            Click on element with no errors and always works
        """
        element = web_driver_waiter.until(EC.element_to_be_clickable((by, value)))
        driver.execute_script("arguments[0].click()", element)

    def get_stocks(self) -> list[PortfolioStock]:
        """
            Gets all stocks user owns on current game session.
        """

        try:
            stocks_list = []

            self.new_page(self.portfolio_url)

            time.sleep(1)
            web_driver_waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cy="holdings-table"]'))) # Wait for table to be loaded

            stocks_list_element = driver.find_elements(By.XPATH, '//*[@id="app"]/div/main/div/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div/div[2]/div/div/table/tbody/tr')
            for stock in stocks_list_element:
                portfolio_stock_data = PortfolioStock()

                portfolio_stock_data.symbol = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="symbol"]').text
                portfolio_stock_data.description = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="description"]').text
                portfolio_stock_data.current_price = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="current-price"]').text 
                portfolio_stock_data.day_change_dollor, portfolio_stock_data.day_change_percent = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="day-gain-dollar"]').text.replace("(","").replace(")","").replace("%","").replace("$","").split("\n")
                portfolio_stock_data.purchase_price = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="purchase-price"]').text
                portfolio_stock_data.quantity = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="quantity"]').text
                portfolio_stock_data.total_value = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="total-value"]').text
                portfolio_stock_data.total_change_dollar, portfolio_stock_data.total_change_percent = stock.find_element(By.CSS_SELECTOR, 'div[data-cy="total-gain-dollar"]').text.replace("(","").replace(")","").replace("%","").replace("$","").split("\n")

                stocks_list.append(portfolio_stock_data)

            return stocks_list
        except:
            pass

    def trade(self, symbol: str, action: Action, quantity: int, order_type: OrderType=OrderType.market, price=0, duration:Duration=Duration.day_only):
        """
            Buys stock
        """
        try:
            self.new_page("/simulator/trade/stocks")

            # SYMBOL
            symbol_input = web_driver_waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Look up Symbol/Company Name"]')))#driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Look up Symbol/Company Name"]')
            symbol_input.send_keys(symbol)
       #     time.sleep(2)
            symbols_list = web_driver_waiter.until(EC.visibility_of_element_located((By.CLASS_NAME, 'v-select-list')))#driver.find_element(By.CLASS_NAME, "v-select-list")
            first_stock = symbols_list.find_element(By.XPATH, "div[1]")

            #first_stock = driver.find_element(By.ID, "list-item-308-0")
            if not first_stock:
                print(f"Could not find symbol {symbol}")
                return None

            first_stock.click()

            # ACTION
            #action_input = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div/div[1]').click()
            web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/main/div/div[2]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div/div[1]'))).click()
            #action_list = web_driver_waiter.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/div')))
            if action.value == 1:
                # Buying
                #driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[1]').click()
                #web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/div/div[1]'))).click()
                self.click_on_element_BY(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[1]')
            elif action.value == 2:
                # Selling
                #driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[4]/div/div[2]').click()
                #rint("selling")
                #web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/div/div[2]'))).click()
                self.click_on_element_BY(By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[2]')

            # QUANTITY
            quantity_input = web_driver_waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[role="select-quantity"]')))#driver.find_element(By.CSS_SELECTOR, 'input[role="select-quantity"]')
            quantity_input.send_keys(quantity)

            # Order Type
            #order_type_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/div/div/div[1]/div[1]/div[1]').click()
            #web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/div/div/div[1]/div[1]/div[1]'))).click()
            #if order_type.value == 1:
            #    #driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[5]/div/div[1]").click()
            #    web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[5]/div/div[1]'))).click()
            #elif order_type.value == 2:
            #    #driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[5]/div/div[2]").click()
            #    web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[5]/div/div[2]'))).click()
            #elif order_type.value == 3:
            #    #driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[5]/div/div[3]").click()
            #    web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[5]/div/div[3]'))).click()

            # Duration
            #duration_button = driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[2]/div/div[2]/div/div/div[1]/div[1]').click()
            #if duration.value == 1:
            #    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[6]/div/div[1]").click()
            #elif duration.value == 2:
            #    driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[6]/div/div[2]").click()

            # Price
            #if order_type.value != 2:
            #    price_input = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/main/div/div[2]/div[2]/div[2]/div[1]/div[2]/form/div[2]/div/div[2]/div/div/div/div[1]/div/input")
            #    if price_input:
            #        price_input.send_keys(price)

            # Preview Order
            #time.sleep(5)
            # driver.find_element(By.XPATH, '//*[@id="app"]/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[3]/div/div[2]/button').click()
            #
            # time.sleep(2)
            self.click_on_element_BY(By.CSS_SELECTOR, 'button[data-cy="preview-button"]')
            #preview_button = web_driver_waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="preview-button"]')))
            ##preview_button.click()
            #driver.execute_script("arguments[0].click()", preview_button)

            time.sleep(1)
            try:
                if driver.find_element(By.CSS_SELECTOR, 'li[data-cy="stock-trade-error"]'):
                    return None, driver.find_element(By.CSS_SELECTOR, 'li[data-cy="stock-trade-error"]').text
            except:
                pass

            # Submit Order
            web_driver_waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="submit-order-button"]'))).click()

            #driver.find_element(By.LINK_TEXT, '/html/body/div[1]/div/div/div[3]/div/div/div[3]/div/div/div[2]').click()

            print(f"Successfully traded {quantity} {symbol} stocks")
        except:
            pass

    def sell_all_owned(self):
        """
            Sells all of your stocks
        """
        
        for stock in self.get_stocks():
            self.trade(stock.symbol, Action.sell, stock.quantity)
"""
    Investopedia API
    Made by Monnapse
"""

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from enum import Enum

wait_time = 20

# DRIVER
options = Options() 

options.headless = True
options.add_argument("--headless=new")

options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options) 
web_driver_waiter = WebDriverWait(driver, wait_time)

class Action(Enum):
    buy = 1
    sell = 2

class Account:
    def __init__(self, username: str, password:str):
        """
            Logs into Investopedia Account
        """

        self.base_url = "https://www.investopedia.com"
        self.portfolio_url = "/simulator/portfolio"

        self.new_page(self.portfolio_url)

        # Sign in
        username_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'username')))
        username_element.send_keys(username)

        password_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'password')))
        password_element.send_keys(password)

        login_element = web_driver_waiter.until(EC.presence_of_element_located((By.ID, 'login')))
        login_element.click()

        time.sleep(1)
        try:
            if driver.find_element(By.CLASS_NAME, "alert-error"):
                # Restart
                self.__init__(username, password)
        except:
            pass

    def new_page(self, url: str):
        driver.get(self.base_url + url)
        time.sleep(1) # Wait for page to be loaded

    def get_account_overview(self):
        """
            Gets Accounts Value, Buying Power, and Cash
        """
        
        self.new_page(self.portfolio_url)
        
        return {
            "account_value": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="account-value-text"]'))).text,
            "buying_power": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="buying-power-text"]'))).text,
            "cash": web_driver_waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-cy="cash-text"]'))).text
        }
    
    def change_game_session(self, session_name: str):
        web_driver_waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="portfolio-select"]'))).click()
        
        list = web_driver_waiter.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[1]/div/div[5]/div/div/div/div')))
        try:
            session = list.find_element(By.XPATH, f"//*[contains(text(), '{session_name}')]")
            session.click()
        except:
            pass

    def click_on_element_BY(self, by: str = By.ID, value: str = None):
        """
            Click on element with no errors and always works
        """
        element = web_driver_waiter.until(EC.element_to_be_clickable((by, value)))
        driver.execute_script("arguments[0].click()", element)

    def trade(self, symbol: str, action: Action, quantity: int):
        """
            Buys stock
        """

        self.new_page("/simulator/trade/stocks")

        # SYMBOL
        symbol_input = web_driver_waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Look up Symbol/Company Name"]')))#driver.find_element(By.CSS_SELECTOR, 'input[placeholder="Look up Symbol/Company Name"]')
        symbol_input.send_keys(symbol)

        symbols_list = web_driver_waiter.until(EC.visibility_of_element_located((By.CLASS_NAME, 'v-select-list')))#driver.find_element(By.CLASS_NAME, "v-select-list")
        first_stock = symbols_list.find_element(By.XPATH, "div[1]")

        if not first_stock:
            return None
        
        first_stock.click()

        # ACTION
        web_driver_waiter.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div/div[1]'))).click()
        if action.value == 1:
            # Buying
            self.click_on_element_BY(By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/div/div[1]')
        elif action.value == 2:
            # Selling
            self.click_on_element_BY(By.XPATH, '/html/body/div[1]/div/div/div/main/div/div[3]/div[2]/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/div/div[2]/div/div[2]')

        # QUANTITY
        quantity_input = web_driver_waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[role="select-quantity"]')))
        quantity_input.send_keys(quantity)

        self.click_on_element_BY(By.CSS_SELECTOR, 'button[data-cy="preview-button"]')

        time.sleep(1)
        try:
            if driver.find_element(By.CSS_SELECTOR, 'li[data-cy="stock-trade-error"]'):
                return None, driver.find_element(By.CSS_SELECTOR, 'li[data-cy="stock-trade-error"]').text
        except:
            pass

        # Submit Order
        web_driver_waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cy="submit-order-button"]'))).click()
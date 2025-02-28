from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.support.ui import Select

import time
import re

import creds

def frostTransfer(amount) :
    # opens up chrome
    driver = webdriver.Chrome()

    # go to the frost home page
    driver.get("https://www.frostbank.com/")

    # finds elements that require login and password then logs into the account
    userNameInput = driver.find_element_by_name("userName")
    passwordInput = driver.find_element_by_name("password")
    userNameInput.send_keys(creds.frostName)
    passwordInput.send_keys(creds.frostPass)
    time.sleep(5)
    driver.find_element_by_id("login-button").click()
    time.sleep(5)

    # moves to the transfer page
    driver.find_element_by_id("tabTransfers").click()

    # the accounts being used in transfer, change these if you have different account names
    accounts = [["Savings"], ["Checking"]] # From -> To

    # element attributes for the drop down menus
    selectors = [["alignFromList", "fromAccountList", "3"], ["alignToList", "toAccountList", "2"]]

    # selects the accounts for both of the drop downs on the page and saves
    # how much money is in the two accounts
    for index, inputBox in enumerate(selectors) :
        fromList = driver.find_element_by_id(inputBox[0])
        fromList.find_element_by_css_selector("[data-id='" + inputBox[1] + "']").click()
        checking = fromList.find_element_by_css_selector("li[data-original-index='" + inputBox[2] + "']")
        option = checking.find_element_by_tag_name("a")
        getDataContent = option.get_attribute("data-normalized-text")
        if getDataContent != None :
            isAccount = re.search(accounts[index][0], getDataContent)
            accounts[index].append((re.search("\$[0-9,]*\.[0-9]*", getDataContent).group()))
            option.click()

    print(accounts)
    amountInput = driver.find_element_by_name("amount")
    amountInput.send_keys(str(amount)) # amount that will be transferred
    memoInput = driver.find_element_by_name("consumerMemo")
    memoInput.send_keys("PayBillsScript")
    driver.find_element_by_id("mma").click() # goes to the final submit page

    # TODO ----------------------------------------
    # Need to send an email from automationseal to laytonseal with a rent rundown
    # Wait for response with a key word

    # once authenticated, click the final submit
    
    # TODO ----------------------------------------

    # logs out of frost when done
    time.sleep(5)
    print("Logging out")
    driver.find_element_by_id("button_logout").click()
    try:
        WebDriverWait(driver, 10).until(EC.title_contains("Log Out"))

    finally:
        driver.quit()

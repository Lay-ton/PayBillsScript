from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re

import creds

def payLeaseRent(amount) :
    # opens up chrome
    driver = webdriver.Chrome()

    # go to the frost home page
    driver.get("https://www.paylease.com/login")

    # logs into the account
    userNameInput = driver.find_element_by_name("email")
    passwordInput = driver.find_element_by_name("password")
    userNameInput.send_keys(creds.payName)
    passwordInput.send_keys(creds.payPass)
    time.sleep(5)
    driver.find_element_by_name("login").click()

    # inputs amount for payment then goes to page for selecting account
    paymentInput = driver.find_element_by_name("payment_amount")
    paymentInput.send_keys(str(amount))
    time.sleep(5)
    driver.find_element_by_name("submit_amount_home").click()

    # selects the bank account and goes to review page
    driver.find_element_by_class_name("existing_bank_acct").click()
    time.sleep(5)
    driver.find_element_by_name("submit_exist_acct").click()

    # submits the payment
    # driver.find_element_by_name("submit_amount").click()

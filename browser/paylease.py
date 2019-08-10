from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import re

import creds

# opens up chrome
driver = webdriver.Chrome()

# go to the frost home page
driver.get("https://www.paylease.com/registration/pay_portal/10735512/ACC?vpw=1482")

# logs into the account
userNameInput = driver.find_element_by_name("email")
passwordInput = driver.find_element_by_name("password")
userNameInput.send_keys(creds.payName)
passwordInput.send_keys(creds.payPass)
time.sleep(5)
driver.find_element_by_name("login").click()

# need to gather how much needs to be paid and send that to frost

#!/usr/bin/env python3

import logging
import os
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

log = logging.getLogger()
log.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

# Export below environment variables and then run this script
# GIVEN_NAME - Given name
# SURNAME - surname
# DOB - date of birth in dd/mm/yyyy format
# EMAIL - email address
# PASSPORT_NUMBER - passport number

given_name = os.environ["GIVEN_NAME"]
sur_name = os.environ["SURNAME"]
dob = os.environ["DOB"]
nationality = os.environ.get("NATIONALITY", "India, Republic of")
email = os.environ["EMAIL"]
passport_number = os.environ["PASSPORT_NUMBER"]
poll_frequency = os.environ.get("POLL_FREQUENCY", 30)

def wait_appointment_list(driver):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table"))
        )
    except:
        log.error("No appointment list coming")
        return(False)
    table = driver.find_element_by_class_name("table")
    rows = table.find_elements_by_tag_name("tr")
    col = rows[0].find_elements_by_tag_name("td")[1]
    if re.match("No appointment\(s\) are currently available", col.text):
        return (False, rows)
    return (True, rows)

def fill_form(driver):
    category = Select(driver.find_element_by_id("Category"))
    category.select_by_visible_text("All")
    subcategory = Select(driver.find_element_by_id("SubCategory")) 
    subcategory.select_by_visible_text("All")
    renew = Select(driver.find_element_by_id("ConfirmGNIB"))
    renew.select_by_visible_text("No")
    driver.find_element_by_id("UsrDeclaration").click()
    gname = driver.find_element_by_id("GivenName")
    gname.clear()
    gname.send_keys(given_name)
    sname = driver.find_element_by_id("SurName")
    sname.clear()
    sname.send_keys(sur_name)

    dob_dom = driver.find_element_by_id("DOB")
    driver.execute_script("arguments[0].value = arguments[1]", dob_dom, dob)

    nationality_dom = Select(driver.find_element_by_id("Nationality"))
    nationality_dom.select_by_visible_text(nationality)

    email_dom = driver.find_element_by_id("Email")
    email_dom.clear()
    email_dom.send_keys(email)


    cemail = driver.find_element_by_id("EmailConfirm")
    cemail.clear()
    cemail.send_keys(email)

    family = Select(driver.find_element_by_id("FamAppYN"))
    family.select_by_visible_text("No")

    passportyn = Select(driver.find_element_by_id("PPNoYN"))
    passportyn.select_by_visible_text("Yes")


    cemail = driver.find_element_by_id("PPNo")
    cemail.clear()
    cemail.send_keys(passport_number)


    driver.find_element_by_id("btLook4App").click()


    date_choice = Select(driver.find_element_by_id("AppSelectChoice"))
    date_choice.select_by_visible_text("closest to today")

    find_slot = driver.find_element_by_id("btSrch4Apps")

    for i in range(10):
        driver.execute_script("arguments[0].click()", find_slot)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        element = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.ID, "btSrch4Apps")))
        appointment, rows = wait_appointment_list(driver)

        if not appointment:
            log.info("No appointment")
            time.sleep(poll_frequency)
        else:
            log.info("Got Appointment")
            return True
    return False


## Start from here
driver = webdriver.Firefox()
driver.get("https://burghquayregistrationoffice.inis.gov.ie/Website/AMSREG/AMSRegWeb.nsf/AppSelect?OpenForm")

#fill_form(driver)
#sys.exit()

while True:
    if fill_form(driver):
        log.info("Got Appointment now")
        driver.maximize_window()
        break

    driver.refresh()

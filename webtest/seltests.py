from django_selenium.testcases import SeleniumTestCase

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time

class BaseSeleniumTextCase(SeleniumTestCase):

    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True

    def is_text_present (self, string):
        if str(string) in self.driver.page_source:
            return True
        else:
            return False

class Examples(BaseSeleniumTextCase):

    def test_pricecheck(self):
        driver = self.driver
        driver.get('/')
        driver.find_element_by_link_text("Try the Examples").click()
        driver.find_element_by_link_text("PriceCheck demo").click()
        driver.find_element_by_id("id_quantity").clear()
        driver.find_element_by_id("id_quantity").send_keys("4")
        driver.find_element_by_id("call_api").click()
        self.is_text_present("total in EUR")
        driver.find_element_by_xpath("//button[@type='button']").click()
        self.is_text_present('"call":"PRICECHECK",')

    def test_purchase_flight(self):
        driver = self.driver
        driver.get('/')
        driver.find_element_by_link_text("Examples").click()
        self.is_text_present('Purchase Flight (buy by weight)')
        driver.find_element_by_link_text("Purchase Flight (buy by weight)").click()
        for i in range(60):
            try:
                if self.is_element_present(By.XPATH, "//tr[td>0]/td[@id=\"carbon\"]"):
                    break
            except: pass
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_xpath("//span[@id='approvePay']").click()
        self.is_text_present("Successfully paid")
        driver.find_element_by_xpath("//button[@type='button']").click()

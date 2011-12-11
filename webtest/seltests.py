from selenium.common.exceptions import NoSuchElementException
from django_selenium.testcases import SeleniumTestCase

from selenium.webdriver.common.by import By
import time

class BaseSeleniumTextCase(SeleniumTestCase):

    def setUp(self):
        super(BaseSeleniumTextCase, self).setUp()
        self.auth_url = "http://testuser:silicon@transactcarbon.com/"
        self.base_url = "http://transactcarbon.com"
        self.driver.get(self.auth_url)
    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True
    def get_relative(self, url):
        self.driver.get(self.base_url + url)

class Examples(BaseSeleniumTextCase):

    def test_pricecheck(self):
        driver = self.driver
        self.get_relative('/')
        driver.find_element_by_link_text("Try the Examples").click()
        driver.find_element_by_link_text("PriceCheck demo").click()
        driver.find_element_by_id("id_quantity").clear()
        driver.find_element_by_id("id_quantity").send_keys("4")
        driver.find_element_by_id("call_api").click()
        driver.is_text_present("total in EUR")
        driver.find_element_by_xpath("//button[@type='button']").click()
        driver.is_text_present('"call":"PRICECHECK",')

    def test_purchase_flight(self):
        driver = self.driver
        self.get_relative('/')
        driver.find_element_by_link_text("Examples").click()
        driver.is_text_present('Purchase Flight (buy by weight)')
        driver.find_element_by_link_text("Purchase Flight (buy by weight)").click()
        for i in range(60):
            if self.is_element_present(By.XPATH, "//tr[td>0]/td[@id=\"carbon\"]"):
                break
            time.sleep(1)
        else:
            self.fail("time out")
        driver.find_element_by_xpath("//span[@id='approvePay']").click()
        driver.is_text_present("Successfully paid")
        driver.find_element_by_xpath("//button[@type='button']").click()

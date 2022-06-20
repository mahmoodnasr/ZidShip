from time import sleep

from bs4 import BeautifulSoup
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class Tracker(object):
    '''
        This class contains the common features of each of the below trackers
        Each has the following Attributes:
            tracking_no: Tracking number of the shipment
            page: Raw HTML data of the page
            tracking_data: A list of checkpoints of the shipment
            status: The current/overall status of the shipment
    '''

    def __init__(self, package):
        '''
            Returns a Scraper Object containing the above Attributes
        '''
        self.tracking_no = package.track_number
        self.courier = package.courier
        self.page = None
        self.tracking_data = []
        self.status = None

    def wait_till_page_load(self, driver, max_wait_time):
        '''
            This method pauses execution until the page is loaded fully, including
            data delayed by JavaScript
        '''
        sleepCount = max_wait_time  # wait for a fixed max_wait_time only

        # A page that's fully loaded has the word 'Current Status'

        while self.tracking_no not in driver.page_source:
            sleep(1)
            sleepCount -= 1
            if sleepCount is 0:
                raise Exception('Request timed out!')  # if max_wait_time is exceeded!

    def remove_non_ascii(self, str_to_clean):
        return ''.join([x for x in str_to_clean if ord(x) < 128])

    def Get_Page(self):
        '''
            Fetches raw HTML data from the site for a given tracking_no
        '''

        # Simply encode the correct url as a string
        url = self.courier.tracking_url + self.tracking_no

        chrome_options = Options()
        chrome_options.add_argument("--headless")

        driver = webdriver.Chrome(ChromeDriverManager().install(),
                                  options=chrome_options)  # create a selenium webdriver
        driver.get(url)  # make it send a request with the above url
        self.wait_till_page_load(driver, 10)  # wait till the page is fully loaded
        self.page = driver.page_source  # store the html source

        driver.quit()  # stop the webdriver

    def Extract_Checkpoints(self):
        '''
            Extract the checkpoints and store in self.tracking_data
        '''

        # Make sure page is available
        if self.page is None:
            raise Exception("The HTML data was not fetched due to some reasons")

        # Check for invalid tracking number
        if self.courier.invalid_clause in self.page:
            raise ValueError('Invalid number/data not currently available')

        # Checkpoints extraction begins here
        for k,v in self.courier.status_mapping.items():
            if v != '' and v in self.page:
                self.status = k
                break

        soup = BeautifulSoup(self.page, 'html.parser')

        # Assign the current status of the shipment - self.status

        track_details = self.get_element(soup, self.courier.track_details_div)

        for row in track_details.findChildren(self.courier.track_details_div.get("tag", "div"), {self.courier.track_details_div.get("attribute", "class"): self.courier.track_details_div.get("child", "trk-wrap")},recursive=True):
            # Get the data
            TD_dict = {}

            TD_dict['location'] = self.get_element_value(row, self.courier.location_div)
            TD_dict['time'] = self.get_element_value(row, self.courier.time_div)
            TD_dict['date'] = self.get_element_value(row, self.courier.date_div)
            TD_dict['status'] = self.get_element_value(row, self.courier.status_div)

            # Add it to the checkpoint list
            self.tracking_data.append(TD_dict)


    def get_element(self, row, element):
        if element.get("attribute","") != "":
            return row.find(element.get("tag", "div"),{element.get("attribute", "class"): element.get("value", "tracking-details")})
        else:
            return row.find(element.get("tag", "div"))

    def get_element_value(self, row, element):
        try:
            element_div = self.get_element(row, element)
            if "child" in element:
                children = element_div.findChildren(element.get("child", "span"), recursive=False)
                for child in children:
                    return self.remove_non_ascii(child.string.strip())
            else:
                return self.remove_non_ascii(element_div.string.strip())
        except:
            return ""

    def Get_Tracking_Data(self):
        '''
            Helper function to get the tracking_data
        '''

        self.Get_Page()
        self.Extract_Checkpoints()
        return {"status": self.status, "data": self.tracking_data}

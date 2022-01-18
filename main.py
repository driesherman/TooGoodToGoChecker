from tgtg import TgtgClient
import json
from pushbullet import Pushbullet
import traceback
import time
import datetime
import requests
import os
import logging


class checker():

    def __init__(self):

        # importing tokens from json
        with open(os.path.join(os.path.dirname(__file__),'tokens.json')) as f:
            self.tokens_dict = json.load(f)

        # setting up the tgtg client
        self.tgtg_client = TgtgClient(access_token=self.tokens_dict["access_token"], refresh_token=self.tokens_dict["refresh_token"], user_id=self.tokens_dict["user_id"])

        # declaring varibiables
        self.timestamp_last_execution = 0
        self.last_date_executed_dict = {}

    # checks if there are any favourites with itmes available
    def check_for_items_available(self):

        # Sometimes requests returns a "104 Connection reset by peer" connection error, this is the handling for it
        try:
            items = self.tgtg_client.get_items()
        
        except ConnectionError:
            pass

        for i in items:

            if i["items_available"] > 0:
                
                store = i["store"]["store_name"]
                items_available = i["items_available"]

                if store in self.last_date_executed_dict and self.last_date_executed_dict[store] == datetime.date.today():
                    continue

                # send notification via Pushbullet
                pb = Pushbullet(self.tokens_dict["pushbullet_token"])
                push = pb.push_note("New TooGoodToGo item available",(f"{store} has {items_available} items available"))

                # add to last executed dict
                self.last_date_executed_dict[store] = datetime.date.today()

    
    # returns nothing, just waits until it succesfully pings Google
    def wait_until_internet_connection(self):

        internet_connection = False

        while not internet_connection:

            try:

                request = requests.get('http://www.google.com', timeout=5)
                internet_connection = True

            except (requests.ConnectionError, requests.Timeout):

                pass
    

    # the main loop of the function
    def loop(self):

        while True:
            
            # wait until connected to the internet
            self.wait_until_internet_connection()

            # setting up the loop so it runs every minute 
            current_timestamp = time.time()
            timestamp_next_execution = self.timestamp_last_execution + 15

            if current_timestamp > timestamp_next_execution:

                self.timestamp_last_execution = current_timestamp
                self.check_for_items_available()

            # sleep until next execution
            time_until_next_execution = timestamp_next_execution - time.time()
            
            if time_until_next_execution > 0:
                time.sleep(time_until_next_execution)


class error_handling:

    def __init__(self):

        # getting the token
        with open(os.path.join(os.path.dirname(__file__),'tokens.json')) as f:
            self.tokens_dict = json.load(f)
        self.pusbullet_api_key = self.tokens_dict["pushbullet_token"]
        self.send_error_messages_pushbullet = True

        # settings for logging
        logging.basicConfig(filename=os.path.join(os.path.dirname(__file__),'logger.log'),filemode='w')


    # deze functie is verantwoordelijk voor het correct handelen van de error moest deze gebeuren
    # indien gecalld print ze de traceback, voegt deze toe aan de logs en stuurt deze op via pushbullet
    def exit_handler(self, error_message):

        print(error_message)

        if self.send_error_messages_pushbullet:

            logging.error(error_message)

            pb = Pushbullet(self.pusbullet_api_key)
            push = pb.push_note("Scraper error",(f"Error message: {error_message}"))



# function that starts it all, with error handling
if __name__ == "__main__":
    
    error = error_handling()

    try:

        mychecker = checker()
        mychecker.loop()

    except Exception:
        error.exit_handler(traceback.format_exc())

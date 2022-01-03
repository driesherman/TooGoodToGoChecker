from tgtg import TgtgClient
import json
from pushbullet import Pushbullet
import traceback
import time
import datetime


class checker():

    def __init__(self):

        # importing tokens from json
        with open('tokens.json') as f:
            self.tokens_dict = json.load(f)

        # setting up the tgtg client
        self.tgtg_client = TgtgClient(access_token=self.tokens_dict["access_token"], refresh_token=self.tokens_dict["refresh_token"], user_id=self.tokens_dict["user_id"])

        # declaring varibiables
        self.timestamp_last_execution = 0
        self.last_date_executed_dict = {}

    # checks if there are any favourites with itmes available
    def check_for_items_available(self):

        items = self.tgtg_client.get_items()

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

    # the main loop of the function
    def loop(self):

        while True:

            # setting up the loop so it runs every minute 
            current_timestamp = time.time()
            timestamp_next_execution = self.timestamp_last_execution + 60

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
        with open('tokens.json') as f:
            self.tokens_dict = json.load(f)
        self.pusbullet_api_key = self.tokens_dict["pushbullet_token"]
        self.send_error_messages_pushbullet = True


    # deze functie is verantwoordelijk voor het correct handelen van de error moest deze gebeuren
    # indien gecalld print ze de traceback, voegt deze toe aan de logs en stuurt deze op via pushbullet
    def exit_handler(self, error_message):

        print(error_message)
        if self.send_error_messages_pushbullet:
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
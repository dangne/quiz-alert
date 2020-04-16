import requests
import time
from objs.account import * 
from objs.web_objects import * 



def main():

    with requests.Session() as ses:
        # Get account info (username + password)
        account = Account()

        # Access login page
        login_page = LoginPage(ses)

        start = time.perf_counter()

        # Login to E-learning and start scanning
        myel = MyELearning(ses, login_page.login(account))

        stop = time.perf_counter()

    print(f'Finish in {stop-start} seconds')

if __name__ == '__main__':
    main()

import requests
from objs.account import * 
from objs.web_objects import * 



def main():

    with requests.Session() as ses:
        # Get account info (username + password)
        account = Account()

        # Access login page
        login_page = LoginPage(ses)

        # Login to E-learning and start scanning
        myel = MyELearning(ses, login_page.login(account))



if __name__ == '__main__':
    main()

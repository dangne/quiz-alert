import requests
from account import Account
from obj import * 



def main():

    with requests.Session() as ses:
        # Get account info (username + password)
        account = Account()

        # Access login page
        login_page = LoginPage(ses)

        # Login to E-learning
        myel = MyELearning(ses, login_page.login(account))

        # Perform scanning
        myel.get_summary()



if __name__ == '__main__':
    main()

# **TooManyTravels telegram bot**

This programme implements a Telegram bot that is designed to search for hotels by user request.

## The bot uses the following commands:

* */lowprice* - to retrieve hotels with a minimum price.
* */highprice* - get hotels with maximum price.
* */bestdeal* - get hotels that match the price/distance ratio
* */help* - get a list of available commands
* */history* - get history of user requests.

## Database

Interaction with the database is implemented within the functionality of the /history command. The project uses a database SQLite, queries written in plain SQL, the interaction with the database itself uses python-library sqlite3.
To create the database, run the **history.py** file. Three tables are implemented in the database: commands (information about commands entered by users), hotels (information about hotels retrieved during command execution) and images (information about images related to retrieved hotels).

## Basic functionality

The project uses the requests library for requests to the Hotels API.  You can read information about the API here: https://rapidapi.com/apidojo/api/hotels4
Also translators library is used to translate city name into English.

## Running the program

Run the **main.py** file, having previously created a database if it doesn't exist.

#### Author: Victor Soloviev

##### 2023, version 1.0

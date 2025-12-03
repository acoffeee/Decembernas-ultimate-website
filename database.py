# Import Peewee
import os
from enum import member
import requests
from dotenv import load_dotenv
from peewee import *
from peewee import IntegrityError
import dotenv
from playhouse.shortcuts import model_to_dict
# Define the database

db = SqliteDatabase('database.db')
# Define a base model class that specifies which database to use
class BaseModel(Model):
    class Meta:
        database = db

# Define a sample table/model
#FOR NOW ITs one large table...
class CARDS(BaseModel):
    username = CharField(null=True)
    userID = IntegerField(null=True)
    cardname = IntegerField(null=True)
    cardID = IntegerField(unique=True)
    userTeamName = CharField(null=True)
    teamID = IntegerField(null=True)
    status = CharField(null=True)
    listedOn = DateField(null=True)
    price = FloatField(null=True)
    imageURL = CharField(null=True)
    type = CharField(null=True)
    saleID = IntegerField(null=True)

# Connect to the database and create tables
def initialize_db():
    db.connect()
    db.drop_tables([CARDS], safe=True)
    db.create_tables([CARDS])
    print("Database and tables created successfully!")
    db.close()

# Example usage
def getPage(page, page_size, request):
    try:
        with db:
            # Start base query
            query = CARDS.select()

            # Get all query params except page/page_size
            params = dict(request.query_params)
            params.pop("page", None)
            params.pop("page_size", None)

            # Apply each filter dynamically
            for key, value in params.items():
                if hasattr(CARDS, key) and value:
                    query = query.where(getattr(CARDS, key) == value)

            total_cards = query.count()
            total_pages = (total_cards + page_size - 1) // page_size
            offset = (page - 1) * page_size

            cards_query = query.limit(page_size).offset(offset)
            cards_list = []
            for card in cards_query:
                card_dict = model_to_dict(card)
                if getattr(card, "listedOn", None):
                    card_dict["listedOn"] = card.listedOn.isoformat()
                cards_list.append(card_dict)

        return {
            "cards": cards_list,
            "current_page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_cards": total_cards
        }

    except Exception as e:
        return {"error": str(e)}


def getAllCards():
    db.connect()
    cards_list = []
    for card in CARDS.select():
        # Convert model to dict
        card_dict = model_to_dict(card)  # requires: from playhouse.shortcuts import model_to_dict

        # Convert listedOn to ISO string if it exists
        if hasattr(card, "listedOn") and card.listedOn is not None:
            card_dict["listedOn"] = card.listedOn.isoformat()

        cards_list.append(card_dict)
    db.close()
    return cards_list

    # Example: add a user
def refreshAllData():
    load_dotenv()
    AUTH_TOKEN = os.getenv("ACCESS_TOKEN")
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Authorization': 'Bearer {token}'.format(token=AUTH_TOKEN)
    }
    db.connect()
    CARDS.delete().execute()
    for teamID in range(1,15):
        url = "http://46.224.62.71:8080/api/teams/" + str(teamID)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            team = response.json()
            for member in team["members"]:
                for entry in member["card_offers"]:
                    CARDS.create(
                        teamID = team["id"],
                        userTeamName = team["name"],
                        username=member["username"],
                        userID=member["id"],
                        cardname=entry["card"]["name"],
                        cardID=entry["card"]["id"],
                        type=entry["card"]["type"],
                        imageURL=entry["card"]["url"],
                        saleID=entry["id"],
                        price=entry["price"],
                        listedOn=entry["submitted_on"],
                        status= "Available"
                    )
                for card in member["cards"]:
                    try:
                        CARDS.create(
                            teamID = team["id"],
                            userTeamName = team["name"],
                            username=member["username"],
                            userID=member["id"],
                            cardname=card["name"],
                            cardID=card["id"],
                            type=card["type"],
                            imageURL=card["url"],
                            status= "Owned"
                        )
                    except IntegrityError:
                        pass
        else:
            print("Error:", response.status_code)
    db.close()
if __name__ == "__main__":
    initialize_db()
    refreshAllData()
    db.close()
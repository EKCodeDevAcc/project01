import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    f = open("zips.csv")
    reader = csv.reader(f)
    for zipcode, city, state, latitude, longitude, population in reader:
        db.execute("INSERT INTO zips (zipcode, city, state, latitude, longitude, population) VALUES (:zipcode, :city, :state, :latitude, :longitude, :population)", {"zipcode": zipcode, "city": city, "state": state, "latitude": latitude, "longitude": longitude, "population": population})
        print(f"Added zipcode {zipcode} of city {city} of state {state} with latitude {latitude}, longitude {longitude}, and {population} people.")

    db.commit()

if __name__ == "__main__":
    main()
import psycopg2
import os
import json


def main():
    full_path = os.path.dirname(os.path.realpath(__file__))
    creds = json.load(open(f'{full_path}/../creds.json', 'r'))

    try:
        conn = psycopg2.connect(
            host=creds["host"],
            database=creds["database"],
            user=creds["user"],
            password=creds["password"])
    except BaseException:
        print("could not connect to db")

    curr = conn.cursor()

    tearDownTables(curr, conn)
    setupTables(curr, conn)

    curr.close()
    conn.close()


def setupTables(cursor, conn):
    fighter_table = """
        CREATE TABLE fighters(
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            tier CHARACTER(1),
            asof DATE
        )
        """

    match_table = """
        CREATE TABLE matches(
            id SERIAL PRIMARY KEY,
            date INTEGER NOT NULL,
            fighter_1 INTEGER NOT NULL,
            fighter_2 INTEGER NOT NULL,
            winner INTEGER NOT NULL,
            bet_1 INT,
            bet_2 INT,
            format VARCHAR(255),
            FOREIGN KEY (fighter_1) REFERENCES fighters(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (fighter_2) REFERENCES fighters(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (winner) REFERENCES fighters(id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (date) REFERENCES dates(id) ON UPDATE CASCADE ON DELETE CASCADE
        )
        """

    date_table = """
        CREATE TABLE dates(
            id SERIAL PRIMARY KEY,
            time TIME,
            date DATE,
            day_of_week VARCHAR(255),
            month VARCHAR(255),
            year INT            
        )
        """

    createTable(cursor, fighter_table, "fighters")
    createTable(cursor, date_table, "dates")
    createTable(cursor, match_table, "matches")
    conn.commit()

def createTable(cursor, table_query, table_name):
    print(f"Creating {table_name} table...")
    cursor.execute(table_query)


def tearDownTables(cursor, conn):
    print("Dropping tables...")
    deleteTable(cursor, "fighters")
    deleteTable(cursor, "dates")
    deleteTable(cursor, "matches")
    conn.commit()


def deleteTable(cursor, table_name):
    print(f"Dropping Table {table_name}...")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")


if __name__ == '__main__':
    main()

import psycopg2
import os
import json
import argparse
import datetime
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dump", help="Dump the databse to ./dumps", action="store_true")
    parser.add_argument("-r", "--reset", help="Resets tables", action="store_true")
    parser.add_argument("-p", "--populate", help="Poplates tables using specified dumps directory", nargs=1, type=str)
    args = parser.parse_args()

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

    if (args.dump):
        dumpTables(curr, full_path)

    if (args.reset):
        tearDownTables(curr, conn)
        setupTables(curr, conn)

    if (args.populate):
        populate_tables(curr, conn, full_path, args.populate[0])

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


def dumpTables(cursor, full_path):
    # Make new directory
    new_dir_name = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-').split('.')[0]
    dump_path = f"{full_path}/dumps/{new_dir_name}"

    if not os.path.exists(dump_path):
        os.makedirs(dump_path)

    tables_to_dump = ["matches", "dates", "fighters"]

    for table_name in tables_to_dump:
        dump_table(cursor, dump_path, table_name)


def dump_table(cursor, dump_path, table_name):
    cursor.execute(f'SELECT * FROM {table_name}')
    new_file = f"{dump_path}/{table_name}.sql"
    print(f"Dumping table {table_name} to {new_file}")

    with open(new_file, 'w') as dump_file:
        for row in cursor:
            row = eval_row(row)
            strRow = str(row)

            if table_name == 'fighters' and '"' in strRow:
                tempRow = strRow.split(', ')
                tempRow[1] = tempRow[1].replace("'", "''").replace('"', "'")
                strRow = ', '.join(tempRow)

            dump_file.write(f"INSERT INTO {table_name} VALUES {strRow};\n")


def eval_row(row):
    evaled_tuple = []
    for tup_item in row:
        if isinstance(tup_item, datetime.date) or isinstance(tup_item, datetime.time):
            evaled_tuple.append(str(tup_item))
        else:
            evaled_tuple.append(tup_item)
    return tuple(evaled_tuple)


def populate_tables(curr, conn, full_path, dump_path):
    full_dump_path = f"{full_path}/{dump_path}"

    if not os.path.isdir(full_dump_path):
        print(f"{full_dump_path} is not a directory!")
        return

    files_expected = ["dates.sql", "fighters.sql", "matches.sql"]
    files_in_dump_path = os.listdir(full_dump_path)

    if (set(files_expected) != set(files_in_dump_path)):
        print(f"Dump path does not contain exactly the following files: {files_expected}")
        return

    for table_sql_file_name in files_expected:
        populate_table(curr, f"{full_dump_path}/{table_sql_file_name}", table_sql_file_name[:-4], conn)


def populate_table(curr, query_file_path, table_name, conn):
    print(f"Populating table {table_name} using {query_file_path}")

    num_rows = sum(1 for line in open(query_file_path, 'r'))
    num_inputs = 0
    with open(query_file_path, 'r') as query_file:
        for row in query_file:
            curr.execute(row)
            num_inputs += 1

            if num_inputs % 100 == 0:
                if num_inputs != 100:
                    sys.stdout.write("\033[K")
                print(f"Pushed {num_inputs}/{num_rows} rows up to {table_name}...", end='\r')
                conn.commit()

    sys.stdout.write("\033[K")
    conn.commit()
    print(f"Pushed {num_inputs}/{num_rows} rows up to {table_name}. Done.")


if __name__ == '__main__':
    main()

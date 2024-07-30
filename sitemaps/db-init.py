import sqlite3

# Create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f'Connected to {db_file}')
    except sqlite3.Error as e:
        print(e)
    return conn

# Create a table for URLs

def create_table(conn):
    sql_drop_table = '''
    DROP TABLE IF EXISTS urls;
    '''
    sql_create_urls_table = '''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE,
        parent_id INTEGER,
        depth INTEGER,
        FOREIGN KEY (parent_id) REFERENCES urls (id) ON DELETE CASCADE
    );
    '''
    try:
        cursor = conn.cursor()
        cursor.execute(sql_drop_table)  # Drop table if it exists
        cursor.execute(sql_create_urls_table)  # Create a new table
    except sqlite3.Error as e:
        print(e)

if __name__ == '__main__':
    database = 'urls.db'

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn:
        create_table(conn)
        conn.close()

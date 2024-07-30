import sqlite3

# Create a database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f'Connected to {db_file}')
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
    return conn

# Insert a new URL into the urls table
def insert_url(url, parent_id, depth, conn):
    if conn is None:
        print("Error: Database connection is not established.")
        return None

    sql_insert = '''
    INSERT OR IGNORE INTO urls(url, parent_id, depth)
    VALUES(?, ?, ?);
    '''
    sql_select = '''
    SELECT id FROM urls WHERE url = ?;
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql_insert, (url, parent_id, depth))
        conn.commit()
        if cur.rowcount > 0:
            last_id = cur.lastrowid
        else:
            cur.execute(sql_select, (url,))
            result = cur.fetchone()
            last_id = result[0] if result else None
        print(f"id: {last_id}, parent_id: {parent_id}, depth: {depth}, url: {url}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        last_id = None
    return last_id

# Fetch the URL tree structure
def fetch_tree(conn):
    if conn is None:
        print("Error: Database connection is not established.")
        return None

    sql = '''
    WITH RECURSIVE url_tree(id, url, parent_id, depth) AS (
        SELECT id, url, parent_id, depth FROM urls WHERE parent_id IS NULL
        UNION ALL
        SELECT u.id, u.url, u.parent_id, u.depth
        FROM urls u
        INNER JOIN url_tree ut ON ut.id = u.parent_id
    )
    SELECT * FROM url_tree;
    '''
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        rows = None
    return rows
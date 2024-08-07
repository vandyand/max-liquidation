import sys
import os

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import sqlite3
from db_init import create_connection

def create_crud_functions(table_name):
    
    def insert(data, conn=None):
        conn_flag = False
        
        if conn is None:
            conn = create_connection()
            conn_flag = True

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql_insert = f'''
        INSERT INTO {table_name}({columns})
        VALUES({placeholders});
        '''
        
        try:
            cur = conn.cursor()
            cur.execute(sql_insert, tuple(data.values()))
            conn.commit()
            lastrowid = cur.lastrowid
            return lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            raise
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()
    
    def insert_or_ignore(data, conn=None):
        conn_flag = False
        
        if conn is None:
            conn = create_connection()
            conn_flag = True

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql_insert = f'''
        INSERT OR IGNORE INTO {table_name}({columns})
        VALUES({placeholders});
        '''
        
        try:
            cur = conn.cursor()
            cur.execute(sql_insert, tuple(data.values()))
            conn.commit()
            lastrowid = cur.lastrowid
            return lastrowid
        except sqlite3.IntegrityError as e:
            print(f"Integrity error: {e}")
            raise
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    def get_all(conn=None):
        conn_flag = False
        if conn is None:
            conn = create_connection()
            conn_flag = True

        sql = f'''
        SELECT * FROM {table_name};
        '''
        try:
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    def get_by_id(record_id, conn=None):
        conn_flag = False
        if conn is None:
            conn = create_connection()
            conn_flag = True

        sql = f'''
        SELECT * FROM {table_name} WHERE id = ?;
        '''
        try:
            cur = conn.cursor()
            cur.execute(sql, (record_id,))
            row = cur.fetchone()
            return row
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    def get_by_column(column_name, value, conn=None):
        conn_flag = False
        
        if conn is None:
            conn = create_connection()
            conn_flag = True

        sql = f'''
        SELECT * FROM {table_name} WHERE {column_name} = ?;
        '''
        
        try:
            cur = conn.cursor()
            cur.execute(sql, (value,))
            row = cur.fetchone()
            return row
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    def update(record_id, data, conn=None):
        conn_flag = False
        if conn is None:
            conn = create_connection()
            conn_flag = True

        columns = ', '.join([f"{key} = ?" for key in data.keys()])
        sql_update = f'''
        UPDATE {table_name}
        SET {columns}
        WHERE id = ?;
        '''
        try:
            cur = conn.cursor()
            cur.execute(sql_update, tuple(data.values()) + (record_id,))
            conn.commit()
            rowcount = cur.rowcount
            return rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    def delete(record_id, conn=None):
        conn_flag = False
        if conn is None:
            conn = create_connection()
            conn_flag = True

        sql_delete = f'''
        DELETE FROM {table_name} WHERE id = ?;
        '''
        try:
            cur = conn.cursor()
            cur.execute(sql_delete, (record_id,))
            conn.commit()
            rowcount = cur.rowcount
            return rowcount
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn_flag:
                conn.close()

    return {
        'insert': insert,
        'insert_or_ignore': insert_or_ignore,
        'get_all': get_all,
        'get_by_id': get_by_id,
        'get_by_column': get_by_column,
        'update': update,
        'delete': delete
    }

def delete_database(test=False):
    db_file = os.getenv('TEST_DB_PATH') if test else os.getenv('DB_PATH')
    
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Database {db_file} deleted successfully.")
        except OSError as e:
            print(f"Error deleting database {db_file}: {e}")
    else:
        print(f"Database {db_file} does not exist.")
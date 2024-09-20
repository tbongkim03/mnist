def connect():
    import os, pymysql
    conn = pymysql.connect(
            host = os.getenv("DB_IP", "localhost"),
            user = 'mnist',
            passwd = '1234',
            db = 'mnistdb',
            charset = 'utf8',
            port = int(os.getenv("DB_PORT", "53306"))
    )
    return conn

def select(query: str, size: int):
    conn = connect()
    import pymysql
    with conn:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Read a single record
            cursor.execute(query)
            if size == -1:
                result = cursor.fetchall()
            else:
                result = cursor.fetchmany(size)
    return result

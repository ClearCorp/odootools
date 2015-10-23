#! /usr/bin/python3

from . import connection


def listAllDatabases(cursor, rolname):
    """Returns a list of databases"""
    cursor.execute("""SELECT datname
FROM pg_database JOIN pg_authid ON pg_database.datdba = pg_authid.oid
WHERE rolname = %s AND NOT datname ilike %s""", (rolname, '%\_pruebas'))
    result = cursor.fetchall()
    return [obj[0] for obj in result]


def getAllUsers(cursor, db_name):
    """Returns all data from users
    per database given"""
    cursor.execute("""SELECT usr.id, partner.name,
  usr.login, usr.login_date,
  usr.active
FROM res_users AS usr, res_partner partner
WHERE partner.id = usr.partner_id
AND usr.share = FALSE
AND usr.login != 'admin'
AND usr.login NOT LIKE '%clearcorp%' ORDER BY partner.name;""")
    return cursor.fetchall()


def getUsersData(host, main_db, user, password, role):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
        host, main_db, user, password)
    # print("Connecting to database -> %s" % main_db)

    # get a connection, if a connect cannot be made an exception will be raised
    conn = connection.connect(conn_string)
    cursor = connection.getDictCursor(conn)
    databases = listAllDatabases(cursor, role)
    cursor.close()
    conn.close()

    data = {}
    for database in databases:
        conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
            host, database, user, password)
        # print("Connecting to database -> %s" % database)
        conn = connection.connect(conn_string)
        cursor = connection.getDictCursor(conn)
        users = getAllUsers(cursor, database)
        data[database] = users
        cursor.close()
        conn.close()
    return data

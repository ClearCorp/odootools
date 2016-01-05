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
    try:
        print(db_name)
        cursor.execute("""SELECT usr.id,
  (SELECT imd.module || '.' ||imd.name AS xml_id
   FROM ir_model_data AS imd
   WHERE imd.model = 'res.users'
   AND imd.res_id = usr.id) AS xml_id, partner.name,
  usr.login, usr.login_date,
  usr.active
FROM res_users AS usr, res_partner AS partner
WHERE partner.id = usr.partner_id
AND usr.share = FALSE 
AND usr.login != 'admin'
AND usr.login NOT LIKE '%clearcorp%' ORDER BY partner.name;""")
        return cursor.fetchall()
    except:
        return {}

def getUsersData(host, main_db, user, password, role):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (
        host, main_db, user, password)

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
        conn = connection.connect(conn_string)
        cursor = connection.getDictCursor(conn)
        users = getAllUsers(cursor, database)
        data[database] = users
        cursor.close()
        conn.close()
    return data

import creds
import pymysql

db = pymysql.connect("localhost","root", creds.emailPass ,"financeDB")

cursor = db.cursor()

# Get the date from the system, break it down into Year, Month, Day
# Check to see if that year-month exist in the database already
#   If it does, check if it has been paid already
#   If it hasn't been paid, find out what is missing and check the emails.
#       If none of the bills are NULL/empty, add them up and fill in total rent
#           Pass total to frost.py func
#           Set up duo for confirmation
#           Check for transfer confirmation email
#           Pass total to paylease.py func
#           Check for receipt email
#           If receipt, mark as paid and put the date in the datebase. END
#   If it doesn't, create a new entry for that year-month
#       Check the emails to see if any are already in
#       If none of the bills are NULL/empty, add them up and fill in total rent
#           Pass total to frost.py func
#           Set up duo for confirmation
#           Check for transfer confirmation email
#           Pass total to paylease.py func
#           Check for receipt email
#           If receipt, mark as paid and put the date in the datebase. END

# Need a to get date from system and break it up like this
date = [ '2019', '08', '19' ]

query = "SELECT * FROM bills WHERE MONTH = '%s-%s'" % (date[0], date[1])
newEntry = """INSERT INTO bills (MONTH, PAID, RENT) VALUES ('2019-08', 0, 940.00)"""

try:

    cursor.execute(query)
    # Checks if entry for that month exists and create a new entry if it doesn't
    if cursor.rowcount == 0 :
        cursor.execute(newEntry)
        db.commit()
        cursor.execute(query)


    print("ROW COUNT: %i" % (cursor.rowcount))
    result = cursor.fetchone()
    if result[1] != 1 :
        for column in result :
            print(column)

    # Commit your changes in the database
    # db.commit()
except:
    # Rollback in case there is any error
    print("Query not found")

# disconnect from server
db.close()

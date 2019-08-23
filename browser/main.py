import pymysql

import creds
import readMail
import frost

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
date = [ '2019', '08', '22' ]

query = "SELECT * FROM bills WHERE MONTH = '%s-%s'" % (date[0], date[1])
newEntry = """INSERT INTO bills (MONTH, PAID, RENT) VALUES ('2019-08', 0, 942.95)"""
bills = []

try:

    cursor.execute(query)
    # Checks if entry for that month exists and create a new entry if it doesn't
    if cursor.rowcount == 0 :
        cursor.execute(newEntry)
        db.commit()
        cursor.execute(query)


    print("ROW COUNT: %i" % (cursor.rowcount))
    # Queries for the row that correlates with system date
    result = list(cursor.fetchone())

    # Checks email for bills
    if result[1] != 1 :
        if result[5] == None : # SPECTRUM
            spectrum = readMail.getSpectrumBill()
            if spectrum != None :
                result[5] = float(spectrum[1])
                bills.append(('SPECTRUM', spectrum[1]))
        if result[6] == None : # WATER
            water = readMail.getWaterBill()
            if water != None :
                result[6] = float(water[1])
                bills.append(('WATER', water[1]))
        if result[7] == None : # ELECTRIC
            electric = readMail.getElectricBill()
            if electric != None :
                result[7] = float(electric[1])
                bills.append(('ELECTRIC', electric[1]))

        # Gets all the bills found in the email and adds them to database
        if len(bills) != 0 :
            insert = []
            for bill in bills :
                insert.append("%s = %s" % (bill[0], bill[1]))
            insert = ", ".join(insert)
            insertBills = "UPDATE bills SET %s WHERE MONTH = '%s-%s'" % (insert, date[0], date[1])
            cursor.execute(insertBills)
            db.commit()

        # If all bills are present, calculate the total to be paid and set it in the database
        if result[5] and result[6] and result[7] :
            totalPaid = float(result[4])
            for item in result[5:] :
                totalPaid += item
            totalPaid = round(totalPaid, 2)
            insertTotal = "UPDATE bills SET TOTAL_PAID = %f WHERE MONTH = '%s-%s'" % (totalPaid, date[0], date[1])
            cursor.execute(insertTotal)
            db.commit()

            # Transfer & Pay Rent and Water
            print("TRANSFER")
            # frost.frostTransfer(totalPaid)

            # Get the paylease reciept then mark paid with 1 and set the paid date
            print("PAY RENT & WATER")
            rentWater = float(result[4]) + float(result[6])
            # paylease.payLeaseRent(rentWater)

            # Look through email for reciept then mark as paid and set date
            fullDate = "-".join(date)
            insertPaid = "UPDATE bills SET PAID = 1, DATE_PAID = '%s' WHERE MONTH = '%s-%s'" % (fullDate, date[0], date[1])
            cursor.execute(insertPaid)
            db.commit()

except:
    # Rollback in case there is any error
    print("Query not found")

# disconnect from server
db.close()

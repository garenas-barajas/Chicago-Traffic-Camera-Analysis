#
# Name: Giancarlos A. Arenas-Barajas
# Class: CS 341
# Assignment: Project 1 – Chicago Traffic Camera Analysis
# Description:
#       Project 1 will present a menu with 9 options that will help the user 
#       gather information from the chicago traffic cameras database

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

##################################################################  
#
# print_stats
#
# Given a connection to the database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    
    print("General Statistics:")
    
    dbCursor.execute("SELECT COUNT(*) FROM RedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Cameras:", f"{row[0]:,}")

    # Display number of speed cameras
    dbCursor.execute("SELECT COUNT(*) FROM SpeedCameras;")
    row = dbCursor.fetchone()
    print("  Number of Speed Cameras:", f"{row[0]:,}")

    # Display number of Red light camera violations 
    dbCursor.execute("SELECT COUNT(*) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Red Light Camera Violation Entries:", f"{row[0]:,}")

    # Display number of speed camera violations
    dbCursor.execute("SELECT COUNT(*) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Number of Speed Camera Violation Entries:", f"{row[0]:,}")

    # Display range of dates in database
    dbCursor.execute("SELECT MIN(Violation_Date), MAX(Violation_Date) FROM SpeedViolations;")
    row = dbCursor.fetchone()
    print("  Range of Dates in the Database:", f"{row[0]} - {row[1]}")

    # Display the total number of speed camera violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM RedViolations;")
    row = dbCursor.fetchone()
    print("  Total Number of Red Light Camera Violations:", f"{row[0]:,}")

    # Display the total number of speed camera violations
    dbCursor.execute("SELECT SUM(Num_Violations) FROM SpeedViolations")
    row = dbCursor.fetchone()
    print("  Total Number of Speed Camera Violations:", f"{row[0]:,}")
    
##################################################################  
#
# function to handle user input
def user_choice():
    while(True):

        print("Select a menu option: ")
        print("  1. Find an intersection by name")
        print("  2. Find all cameras at an intersection")
        print("  3. Percentage of violations for a specific date")
        print("  4. Number of cameras at each intersection")
        print("  5. Number of violations at each intersection, given a year")
        print("  6. Number of violations by year, given a camera ID")
        print("  7. Number of violations by month, given a camera ID and year")
        print("  8. Compare the number of red light and speed violations, given a year")
        print("  9. Find cameras located on a street")
        print("or x to exit the program.")

        # holds user choice
        choice = input("Your choice -->")

        if choice == '1':
            findIntersections(dbConn)
        elif choice == '2':
            findAllCameras(dbConn)
        elif choice == '3':
            percentageViolations(dbConn)
        elif choice == '4':
            numCameras(dbConn)
        elif choice == '5':
            numViolationsInYear(dbConn)
        elif choice == '6':
            numViolationsByYearID(dbConn)
        elif choice == '7':
            numViolationsByMonthIDYear(dbConn)
        elif choice == '8':
            compareRedSpeedViolations(dbConn)
        elif choice == '9':
            findCamerasOnStreet(dbConn)
        elif choice == 'x':
            print(' Exiting program.')
            break
        else:
            print(' Error, unknown command, try again...\n')
    
##################################################################  
#
# Function to find all intersections based on user input.
def findIntersections(dbConn):
    # Get user choice for intersection name
    intersection = input("\nEnter the name of the intersection to find (wildcards _ and % allowed): ")

    # Create a cursor object, cursor is used to execute SQL queries
    dbCursor = dbConn.cursor()

    # SQL query to find intersections based on user input
    sql = """SELECT 
                Intersection_ID, 
                Intersection 
            FROM 
                Intersections 
            WHERE 
                Intersection LIKE ? 
            ORDER BY 
                Intersection"""

    # Execute the query with the user input (wildcards supported)
    dbCursor.execute(sql, (intersection,) )

    # Fetch all matching results
    results = dbCursor.fetchall()

    # Check if there are any results
    if not results:
        print("No intersections matching that name were found.")

    # result in results will iterate through each result in the list
    for result in results:
        # print the id and name of the intersection
        print(f"{result[0]} : {result[1]}")

    # Close the cursor
    dbCursor.close()


##################################################################
#
# Function to find all cameras at a given intersection
def findAllCameras(dbConn):
    # Get user choice for intersection ID
    intersection = input("\nEnter the name of the intersection (no wildcards allowed):")

    # Create a cursor object
    dbCursor = dbConn.cursor()

    # SQL Query to find all cameras(speed and redlight) at a given intersection
    sql = """SELECT DISTINCT 
                Camera_ID, 
                Address 
            FROM 
                RedCameras rc
            JOIN
                Intersections i ON rc.Intersection_ID = i.Intersection_ID
            WHERE 
                i.Intersection = ? 
            ORDER BY 
                Camera_ID"""

    # Execute the query with the user input
    dbCursor.execute(sql, (intersection,))

    #Fetch all matching results
    redLightCameras = dbCursor.fetchall()

    # SQL Query to find all cameras(speed and redlight) at a given intersection
    sql = """SELECT DISTINCT 
                Camera_ID, 
                Address 
            FROM 
                SpeedCameras sc
            JOIN
                Intersections i ON sc.Intersection_ID = i.Intersection_ID
            WHERE 
                i.Intersection = ? 
            ORDER BY 
                Camera_ID"""

    # Execute the query with the user input
    dbCursor.execute(sql, (intersection,))

    #Fetch all matching results
    speedCameras = dbCursor.fetchall()

    # Check if there are any results
    if not redLightCameras and not speedCameras:
        print("\nNo red light cameras found at that intersection.")
        print("\nNo speed cameras found at that intersection.\n")
    # Print results
    else:
        if redLightCameras:
            print("\nRed Light Cameras:")
            for camera in redLightCameras:
                print(f"   {camera[0]} : {camera[1]}")
        else:
            print("\nNo red light cameras found at that intersection.")
        
        if speedCameras:
            print("\nSpeed Cameras:")
            for camera in speedCameras:
                print(f"   {camera[0]} : {camera[1]}")
            print()
        else:
            print("\nNo speed cameras found at that intersection.\n")

    dbCursor.close()


#############################################################################################
#
# Function to find the percentage of violations for a specific date
def percentageViolations(dbConn):
    # Get user choice for date
    date = input("\nEnter the date that you would like to look at (format should be YYYY-MM-DD):")

    # Create a cursor object
    dbCursor = dbConn.cursor()

    # SQL Query to find total number of red light violations
    sql = """SELECT
                SUM(Num_Violations)
            FROM
                RedViolations
            WHERE 
                Violation_Date = ?"""

    # Execute the query with user input
    dbCursor.execute(sql, (date,))
    
    # Fetch results
    redViolations = dbCursor.fetchone()

    # try catch block to see if we can convert the value to an integer
    try:
        redViolations = int(redViolations[0])
    except (ValueError, TypeError):
        redViolations = 0

    # SQL Query to find total number of speed violations
    sql = """SELECT
                SUM(Num_Violations)
            FROM
                SpeedViolations
            WHERE
                Violation_Date = ?"""
    
    dbCursor.execute(sql, (date,))

    # Fetch results
    speedViolations = dbCursor.fetchone()

    # Try catch block to see if we can convert the value to an integer
    try:
        speedViolations = int(speedViolations[0])
    except (ValueError, TypeError):
        speedViolations = 0

    totalViolations = redViolations + speedViolations

    # Check if date exists
    if totalViolations == 0:
        print(" No violations on record for that date.\n")
        return
    
    # Compute percentages
    redPercent = (redViolations / totalViolations) * 100
    speedPercent = (speedViolations / totalViolations) * 100

    # Print results
    print(" Number of Red Light Violations:", f"{redViolations:,} ", f"({redPercent:.3f}%)")
    print("Number of Speed Violations:", f"{speedViolations:,} ", f"({speedPercent:.3f}%)")
    print("Total Number of Violations:", f"{totalViolations:,}\n")

    dbCursor.close()



##################################################################
#
# Output the number of cameras at each intersection
def numCameras(dbConn):
    #Create object cursor
    dbCursor = dbConn.cursor()

    #Red light cameras
    sqlRed = """SELECT
                i.Intersection,
                i.Intersection_ID,
                COUNT(rc.Camera_ID) AS numRedCameras
            FROM
                Intersections i
            JOIN
                RedCameras rc ON i.Intersection_ID = rc.Intersection_ID
            GROUP BY
                i.Intersection_ID
            ORDER BY
                numRedCameras DESC
            """
    dbCursor.execute(sqlRed)
    redLightCameras = dbCursor.fetchall()
    
    #Speed cameras
    sqlSpeed = """SELECT
                    i.Intersection,
                    i.Intersection_ID,
                    COUNT(sc.Camera_ID) AS numSpeedCameras
                FROM
                    Intersections i
                JOIN
                    SpeedCameras sc ON i.Intersection_ID = sc.Intersection_ID
                GROUP BY
                    i.Intersection_ID
                ORDER BY
                    numSpeedCameras DESC"""
    dbCursor.execute(sqlSpeed)
    speedCameras = dbCursor.fetchall()

    #Total number of red light cameras
    sqlTotalRed = """SELECT
                        COUNT(*)
                    FROM RedCameras"""
    dbCursor.execute(sqlTotalRed)
    totalRedCameras = dbCursor.fetchone()
    totalRedCameras = totalRedCameras[0]

    #Total number of red light cameras
    sqlTotalSpeed = """SELECT
                        COUNT(*)
                    FROM SpeedCameras"""
    dbCursor.execute(sqlTotalSpeed)
    totalSpeedCameras = dbCursor.fetchone()
    totalSpeedCameras = totalSpeedCameras[0]

    #Total number of cameras
    totalCameras = totalRedCameras + totalSpeedCameras

    # print results
    print("\nNumber of Red Light Cameras at Each Intersection")
    for camera in redLightCameras:
        percentage = (camera[2] / totalRedCameras) * 100 if totalRedCameras > 0 else 0
        print(f"  {camera[0]} ({camera[1]}) : {camera[2]:,} ({percentage:.3f}%)")

    print("\nNumber of Speed Cameras at Each Intersection")
    for camera in speedCameras:
        percentage = (camera[2] / totalSpeedCameras) * 100 if totalSpeedCameras > 0 else 0
        print(f"  {camera[0]} ({camera[1]}) : {camera[2]:,} ({percentage:.3f}%)")
    
    dbCursor.close()

##################################################################
#
# Output the number of violations at each intersection for a given year
def numViolationsInYear(dbConn):
    # Get user input for year
    year = input("\nEnter the year that you would like to analyze:")
    
    # Create a cursor object
    dbCursor = dbConn.cursor()

    # SQL Query to find the number of red light violatios per intersection for a given yer
    sql = """SELECT
                i.Intersection,
                i.Intersection_ID,
                SUM(rv.Num_Violations) AS totalViolations
            FROM 
                Intersections i
            JOIN
                RedCameras rc ON i.Intersection_ID = rc.Intersection_ID
            JOIN
                RedViolations rv ON rc.Camera_ID = rv.Camera_ID
            
            WHERE
                strftime('%Y', rv.Violation_Date) = ?
            GROUP BY
                i.Intersection_ID,
                i.Intersection
            ORDER BY
                totalViolations DESC,
                i.Intersection_ID DESC"""
    dbCursor.execute(sql, (year,))
    redLightIntersections = dbCursor.fetchall()

    # SQL Query to find total red light violations for a given year
    sqlRed = """SELECT
                    SUM(Num_Violations)
                FROM
                    RedViolations
                WHERE
                    strftime('%Y', Violation_Date) = ?"""
    dbCursor.execute(sqlRed, (year,))
    redLightViolations = dbCursor.fetchone()

    # Convert redLightViolations to int
    if redLightIntersections is None or redLightViolations[0] is None:
        redLightViolations = 0
    else:
        redLightViolations = int(redLightViolations[0])
    
     # SQL Query for speed violations per intersection for a given year
    sql = """SELECT
                i.Intersection,
                i.Intersection_ID,
                SUM(sv.Num_Violations) AS totalViolations
            FROM
                Intersections i
            JOIN
                SpeedCameras sc ON i.Intersection_ID = sc.Intersection_ID
            JOIN
                SpeedViolations sv ON sc.Camera_ID = sv.Camera_ID
            WHERE
                strftime('%Y', sv.Violation_Date) = ?
            GROUP BY
                i.Intersection_ID
            ORDER BY
                totalViolations DESC,
                i.Intersection_ID DESC"""
    dbCursor.execute(sql, (year,))
    speedIntersections = dbCursor.fetchall()

    # SQL Query to find total speed violations for a given year
    sqlSpeed = """SELECT
                    SUM(Num_Violations)
                FROM
                    SpeedViolations
                WHERE
                    strftime('%Y', Violation_Date) = ?"""
    dbCursor.execute(sqlSpeed, (year,))
    speedViolations = dbCursor.fetchone()

    # Convert speedViolations to int
    if speedIntersections is None or speedViolations[0] is None:
        speedViolations = 0
    else:
        speedViolations = int(speedViolations[0])

    # Calculate total violations
    totalViolations = redLightViolations + speedViolations

    # Print results
    print("\nNumber of Red Light Violations at Each Intersection for", year)
    if redLightViolations:
        totalRedLightViolations = sum(intersection[2] for intersection in redLightIntersections)
        for intersection in redLightIntersections:
            redPercent = (intersection[2] / totalRedLightViolations) * 100 if totalRedLightViolations > 0 else 0
            print(f"  {intersection[0]} ({intersection[1]}) : {intersection[2] if intersection[2] else 0:,} ({redPercent:.3f}%)")
        print(f"Total Red Light Violations in {year} : {redLightViolations:,}")
    else:
        print("No red light violations on record for that year.")
    
    print("\nNumber of Speed Violations at Each Intersection for", year)
    if speedViolations:
        totalSpeedViolations = sum(intersection[2] for intersection in speedIntersections)
        for intersection in speedIntersections:
            speedPercent = (intersection[2] / totalSpeedViolations) * 100 if totalSpeedViolations > 0 else 0
            print(f"  {intersection[0]} ({intersection[1]}) : {intersection[2] if intersection[2] else 0:,} ({speedPercent:.3f}%)")
        print(f"Total Speed Violations in {year} : {speedViolations:,}\n")
    else:
        print("No speed violations on record for that year.\n")
    
    
    dbCursor.close()

##################################################################
#
# Output the number of violations by year for a given camera ID
def numViolationsByYearID(dbConn):
    # Get user input for camera ID
    cameraID = input("\nEnter a camera ID:")

    # Create cursor object
    dbCursor = dbConn.cursor()

    # Check if camera ID exists in redCameras
    sql = """SELECT
                COUNT(*)
            FROM
                RedCameras
            WHERE
                Camera_ID = ?"""
    dbCursor.execute(sql, (cameraID,))
    redCamera = dbCursor.fetchone()
    redCamera = redCamera[0]

    # Check if camera ID exists in speedCameras
    sql = """SELECT
                COUNT(*)
            FROM
                SpeedCameras
            WHERE
                Camera_ID = ?"""
    dbCursor.execute(sql, (cameraID,))
    speedCamera = dbCursor.fetchone()
    speedCamera = speedCamera[0]

    # Check if camera ID exists in either table
    if speedCamera == 0 and redCamera == 0:
        print(" No cameras matching that ID were found in the database.")
        return

    #SQL Query to find the number of violations recorded by a camera for each year
    sql = """SELECT
                year,
                SUM(totalViolations) AS total
            FROM(  
                SELECT
                    strftime('%Y', Violation_Date) AS year,
                    Num_Violations AS totalViolations
                FROM
                    RedViolations
                WHERE
                    Camera_ID = ?

                UNION ALL
                
                SELECT
                    strftime('%Y', Violation_Date) AS year,
                    Num_Violations AS totalViolations
                FROM
                    SpeedViolations
                WHERE
                    Camera_ID = ?
                ) AS combined
            GROUP BY
                year
            ORDER BY
                year ASC"""
    dbCursor.execute(sql, (cameraID, cameraID))
    numViolations = dbCursor.fetchall()

    print(" Yearly Violations for Camera", cameraID)

    # Variables for plotting
    years = []
    violations = []

    # Print results
    for camera in numViolations:
        print(f"{camera[0]} : {camera[1]:,}")
        years.append(camera[0])
        violations.append(camera[1])
    
    # Plot data
    plot = input("\nPlot? (y/n)\n")

    if plot == 'y':
        # Plot data
        plt.plot(years, violations)

        # Axis labels and title
        plt.xlabel('Year')
        plt.ylabel('Number of Violations')
        plt.title(f'Yearly Violations for Camera {cameraID}')

        plt.show()
        return

    dbCursor.close()

##################################################################
#
# Output the number of violations by month for a given camera ID and year
def numViolationsByMonthIDYear(dbConn):
    # Get user input for camera ID
    cameraID = input("\nEnter a camera ID:")

    # Create cursor object
    dbCursor = dbConn.cursor()

    # Check if camera ID exists in redCameras
    sql = """SELECT
                COUNT(*)
            FROM
                RedCameras
            WHERE
                Camera_ID = ?"""
    dbCursor.execute(sql, (cameraID,))
    redCamera= dbCursor.fetchone()
    redCamera = redCamera[0]

    # Check if camera ID exists in speedCameras
    sql = """SELECT
                COUNT(*)
            FROM
                SpeedCameras
            WHERE
                Camera_ID = ?"""
    dbCursor.execute(sql, (cameraID,))
    speedCamera = dbCursor.fetchone()
    speedCamera = speedCamera[0]
    
    # Check if camera ID exists in either table
    if speedCamera == 0 and redCamera == 0:
        print(" No cameras matching that ID were found in the database.")
        return
    
    # Get user input for year
    year = input(" Enter a year:")
    
    # SQL Query to find the number of violations recorded by a camera for each month
    sql = """SELECT
                strftime('%m/%Y', Violation_Date) AS month,
                SUM(Num_Violations) AS totalViolations
            FROM(
                SELECT
                    Violation_Date,
                    Num_Violations
                FROM 
                    RedViolations
                WHERE
                    Camera_ID = ? AND strftime('%Y', Violation_Date) = ?

                UNION ALL

                SELECT
                    Violation_Date,
                    Num_Violations
                FROM
                    SpeedViolations
                WHERE
                    Camera_ID = ? AND strftime('%Y', Violation_Date) = ?
                ) AS combined
            GROUP BY
                month
            ORDER BY
                month ASC"""
    dbCursor.execute(sql, (cameraID, year, cameraID, year))
    monthlyViolations = dbCursor.fetchall()

    # variables for plotting
    months = []
    violations = []

    # Print results
    print(f" Monthly Violations for Camera {cameraID} in {year}")
    for month in monthlyViolations:
        print(f"{month[0]} : {month[1]:,}")
        months.append(month[0])
        violations.append(month[1])

    # Plot data
    plot = input("\nPlot? (y/n)\n")

    if plot == 'y':
        # Plot data
        plt.plot(months, violations)

        # Axis labels and title
        plt.xlabel('Month')
        plt.ylabel('Number of Violations')
        plt.title(f'Monthly Violations for Camera {cameraID} ({year})')

        plt.show()
        return

    dbCursor.close()
##################################################################
#
# Compare the number of red light and speed violations for a given year
def compareRedSpeedViolations(dbConn):
    # Get user input for year
    year = input("\nEnter a year:")

    # Create cursor object
    dbCursor = dbConn.cursor()

    # SQL Query to find the number of red light violations per day for a given year
    sql = """SELECT
                Violation_Date,
                SUM(Num_Violations) AS totalViolations
            FROM
                RedViolations
            WHERE
                strftime('%Y', Violation_Date) = ?
            GROUP BY
                Violation_Date
            ORDER BY 
                Violation_Date ASC"""
    dbCursor.execute(sql, (year,))
    redViolations = dbCursor.fetchall()

    # SQL Query to find the number of speed violations per day for a given year
    sql = """SELECT
                Violation_Date,
                SUM(Num_Violations) AS totalViolations
            FROM
                SpeedViolations
            WHERE
                strftime('%Y', Violation_Date) = ?
            GROUP BY
                Violation_Date
            ORDER BY
                Violation_Date ASC"""
    dbCursor.execute(sql, (year,))
    speedViolations = dbCursor.fetchall()

    # Variables for plotting
    redLightDates = []
    numRedLightViolations = []
    speedDates = []
    numSpeedViolations = []
    
    # Process data for plotting
    for date, violations in redViolations:
        redLightDates.append(date)
        numRedLightViolations.append(violations)
    
    for date, violations in speedViolations:
        speedDates.append(date)
        numSpeedViolations.append(violations)

    # Get the first and last day of the year
    firstDay = f"{year}-01-01"
    lastDay = f"{year}-12-31"

    # Convert to datetime objects to generate full date range for plotting
    startDate = datetime.strptime(firstDay, "%Y-%m-%d")
    endDate = datetime.strptime(lastDay, "%Y-%m-%d")

    # Create a list of all dates in the range
    allDates = [startDate + timedelta(days=x) for x in range((endDate - startDate).days + 1)]
    # Convert all dates to strings
    allDatesStr = [date.strftime("%Y-%m-%d") for date in allDates]

    # Fill in missing dates
    redViolationsDict = dict(zip(redLightDates, numRedLightViolations))
    speedViolationsDict = dict(zip(speedDates, numSpeedViolations))
    redViolationsFilled = [redViolationsDict.get(date, 0) for date in allDatesStr]
    speedViolationsFilled = [speedViolationsDict.get(date, 0) for date in allDatesStr]

    # Print results: display the first 5 and last 5 rows of violations
    # Prints first 5 red violations
    print(" Red Light Violations:")
    for row in redViolations[:5]:
        print(f"{row[0]} {row[1]}")

    # Prints last 5 red violations
    for row in redViolations[-5:]:
        print(f"{row[0]} {row[1]}")
    
    # Prints first 5 speed violations
    print("Speed Violations:")
    for row in speedViolations[:5]:
        print(f"{row[0]} {row[1]}")
    
    # Prints last 5 speed violations
    for row in speedViolations[-5:]:
        print(f"{row[0]} {row[1]}")

    # Plot data
    plot = input("\nPlot? (y/n)\n")

    if plot == 'y':
        # Plot red light and speed violations
        plt.plot(range(len(allDatesStr)), redViolationsFilled, label='Red Light', color = 'red')
        plt.plot(range(len(allDatesStr)), speedViolationsFilled, label='Speed', color = 'orange')

        # Axis labels and title
        plt.xlabel('Day')
        plt.ylabel('Number of Violations')
        plt.title(f'Violations Each Day of {year}')
        plt.legend()

        # X-axis ticks
        plt.xticks(range(0, len(allDatesStr), 50), [str(i) for i in range(0, 365, 50)])

        plt.show()
        return

    dbCursor.close()
    
##################################################################
#
# Find all cameras located on a street
def findCamerasOnStreet(dbConn):
    # Get user input for street name
    street = input("\nEnter a street name:")

    # Create cursor object
    dbCursor = dbConn.cursor()    
    
    # SQL Query to find all red and speed cameras on that street
    sql =   """
            SELECT
                Camera_ID,
                Address,
                Latitude,
                Longitude
            FROM 
                RedCameras
            WHERE
                Address LIKE ?
            ORDER BY 
                Camera_ID ASC
            """
    dbCursor.execute(sql, (f"%{street}%",))
    redCameras = dbCursor.fetchall()

    # SQL Query to find all speed cameras on that street
    sql =   """
            SELECT
                Camera_ID,
                Address,
                Latitude,
                Longitude
            FROM
                SpeedCameras
            WHERE
                Address LIKE ?
            ORDER BY
                Camera_ID ASC
            """
    dbCursor.execute(sql, (f"%{street}%",))
    speedCameras = dbCursor.fetchall()

    #If no cameras are located on the street entered by the user, display a message to indicate that. 
    if not redCameras and not speedCameras:
        print(f" There are no cameras located on that street.")
        return

    # Print results
    print(f"\nList of Cameras Located on Street:", street)

    print(f"  Red Light Cameras:")
    for camera in redCameras:
        print(f"     {camera[0]} : {camera[1]} ({camera[2]}, {camera[3]})")
    
    print(f"  Speed Cameras:")
    for camera in speedCameras:
        print(f"     {camera[0]} : {camera[1]} ({camera[2]}, {camera[3]})")

    # Plot data
    plot = input("\nPlot? (y/n)\n")

    if plot == 'y':

        # Import image
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]

        plt.imshow(image, extent=xydims)
        plt.title(f"Cameras On Street: {street}")

        # Plot red light cameras
        for camera in redCameras:
            plt.scatter(camera[3], camera[2], color='red', s=10)
            plt.annotate(str(camera[0]), (camera[3], camera[2]))
        
        # Plot speed cameras
        for camera in speedCameras:
            plt.scatter(camera[3], camera[2], color='orange', s=10)
            plt.annotate(str(camera[0]), (camera[3], camera[2]))

        # Set limits
        plt.xlim([-87.9277, -87.5569]) 
        plt.ylim([41.7012, 42.0868]) 
        plt.show() 
    
        dbCursor.close()

##################################################################
#
# main
#
dbConn = sqlite3.connect('chicago-traffic-cameras.db')

print("Project 1: Chicago Traffic Camera Analysis")
print("CS 341, Spring 2025")
print()
print("This application allows you to analyze various")
print("aspects of the Chicago traffic camera database.")
print()
print_stats(dbConn)
print()

# call function to handle user choice
user_choice()

#
# done
#
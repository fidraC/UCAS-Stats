# Crawls the UCAS website, collects data, and stores them in a database
from time import sleep
import requests
import bs4 as bs
import sqlite3
import os
import sys
import json
import traceback

# Courses
class Courses:
    def __init__(self, area, url):
        self.area = area
        self.url = url
        self.courses = []

class Course:
    def __init__(
        self, 
        name, url, course_university=None,
        average_salary=None, course_length=None, fees=None, 
        entry_requirements=None, course_level=None, student_satisfaction=None, employment_rate=None
    ):
        self.name = name
        self.url = url
        self.average_salary = average_salary
        self.course_length = course_length
        self.fees = fees
        self.entry_requirements = entry_requirements
        self.course_level = course_level
        self.student_satisfaction = student_satisfaction
        self.course_university = course_university
        self.employment_rate = employment_rate



# Dynamic crawler
class Crawler:
    def get_soup(url):
        # Get the HTML
        attempts = 0
        while (True and attempts < 5):
            try:
                r = requests.get(url)
                break
            except Exception as e:
                attempts += 1
                print(e)
                sleep(10)
        return bs.BeautifulSoup(r.text, "html.parser")

    def get_element_list(soup, elements):
        data = soup.find_all(elements[0], {'class': elements[1]}, {'id': elements[2]})
        return data

    def get_data_field(element_list, field):
        # Get the href from the data elements
        data = []
        for element in element_list:
            data.append(element[field])
        return data
    
    def get_data_text(element_list):
        # Get the text from the data elements
        data = []
        for element in element_list:
            data.append(element.text)
        if len(data) == 1:
            return data[0]
        else:
            return data

# Main
def get_course_data(area):
    print("Getting course data for " + area)
    # Set area and url
    base_url = "https://www.ucas.com"
    url = base_url + "/explore/courses" + "?subject=" + area
    # Parse URL as url
    url = url.replace(" ", "%20")
    # link crawler
    links = Crawler.get_data_field(
        Crawler.get_element_list(
            Crawler.get_soup(url),
            ['a', 'pagination__link', None]
        ),
        'href'
    )
    courses = Courses(area=area, url=url)
    # Debug use only 1 link
    for link in links:
        print(".")
        soup = Crawler.get_soup(base_url + link)
        course_tiles = Crawler.get_element_list(soup, ['article', 'course-panel', None])
        for course_tile in course_tiles:
            course_title_data = Crawler.get_element_list(
                    course_tile, 
                    ['h3', 'course-title', None]
            )
            
            course_name = Crawler.get_data_text(course_title_data)

            course_university_data = Crawler.get_data_text(
                Crawler.get_element_list(
                        course_tile,
                        ['a', 'provider', None]
                ),
            ).replace("\n", "").replace("  ", "")

            course_url = bs.BeautifulSoup(course_title_data[0].prettify(), "html.parser").a['href']
            
            average_salary = Crawler.get_data_text(
                Crawler.get_element_list(
                    course_tile,
                    ['div', 'salary', None]
                )
            ).replace("Average grad salary", "").replace("£", "").replace(",", "").replace(" ", "")
            
            student_satisfaction = Crawler.get_data_text(
                Crawler.get_element_list(
                    course_tile,
                    ['div', 'satisfaction', None]
                )
            ).replace("Student satisfaction", "").replace("%", "").replace(" ", "")
            course_length = Crawler.get_data_text(
                Crawler.get_element_list(
                    course_tile,
                    ['div', 'duration', None]
                )
            ).replace("Duration", '').replace(" ", '').replace("Years", '').replace("Year", '')

            course_level = Crawler.get_data_text(
                Crawler.get_element_list(
                    course_tile,
                    ['div', 'qualification', None]
                )
            ).replace("Qualification", '').replace(" ", '')

            courses.courses.append(Course(
                name=course_name,
                url=course_url,
                average_salary=average_salary,
                student_satisfaction=student_satisfaction,
                course_length=course_length,
                course_level=course_level,
                course_university=course_university_data
            ))
    # Loop through courses
    # Debug use only 5 courses
    for course in courses.courses:
        print(".")
        soup = Crawler.get_soup(course.url)
        original_soup = soup
        ### Get employment rate
        try:
            employment_rate = Crawler.get_data_text(
                Crawler.get_element_list(
                    soup,
                    ['text', 'percentage', None]
                )
            )[0].replace("%", "").replace(" ", "")
        except:
            employment_rate = "N/A"
        course.employment_rate = employment_rate
        ### Get the course fees ###
        # Get course fees table 
        try:
            course_fees_table = Crawler.get_element_list(
                soup,
                ['table', None, None]
            )[0]
        except:
            continue
        # Get a list of the values in the first and second column of the table
        # The first column contains the location 
        # The second column contains the fees
        # Map the two lists into a json dictionary
        table_rows = Crawler.get_element_list(
            course_fees_table,
            ['tr', None, None]
        )
        # loop through the rows
        # Make dictionary of location and fees
        fees = {}
        for row in table_rows:
            # Get the location
            soup = bs.BeautifulSoup(row.prettify(), "html.parser")
            try:
              location = soup.find('td', {'class': 'column-width--30pc'}).text.replace(" ", "").replace("\n", "")
              fee = soup.find('td', {'class': 'column-width--20pc'}).text.replace(" ", "").replace("\n", "").replace("£", "").replace("*", "").replace("£", "")
            except:
                location = "N/A"
                fee = "N/A"
            # Add to dictionary
            fees[location] = fee
        # Add fees to course as JSON string
        if 'International' in fees:
            course.fees = fees['International']
        else:
            course.fees = str(json.dumps(fees))
        ### Get entry requirements ###
        # Find accordion__label with text "International Baccalaureate Diploma Programme"
        entry_requirements = Crawler.get_element_list(
            original_soup,
            ['h2', 'accordion__label', None]
        )
        # Loop through entry requirements
        for entry_requirement in entry_requirements:
            # Get the text
            text = Crawler.get_data_text(entry_requirement)
            # Check if International Baccalaureate Diploma Programme is in the text
            if "UCAS Tariff" in text:
                print("found!")
                if "points" in text:
                    # Get the points
                    points = text.split("points")[0].split(" ")[-2]
                    # Add to course
                    course.entry_requirements = points
                    # Break out of loop
                    break
                else:
                    course.entry_requirements = "N/A"
                    break
        # replace course entry in courses with new course
        courses.courses[courses.courses.index(course)] = course
        # Insert into database
        try:
            Database.insert(course)
        except Exception as e:
            print(e)
            # Print stack trace
            traceback.print_exc()
    return courses

class Database:
    def create():
        if not os.path.exists(output_file_arg):
            conn = sqlite3.connect(output_file_arg)
            c = conn.cursor()
            c.execute('''CREATE TABLE courses
                (id INTEGER PRIMARY KEY,name text, university text, url text, average_salary text, student_satisfaction text, course_length text, course_level text, fees text, entry_requirements text, employment_rate text)''')
            conn.commit()
            conn.close()
            print("Database created")
        else:
            print("Database already exists")
    def insert(course):
        # Convert all values to strings
        name = str(course.name)
        url = str(course.url)
        average_salary = str(course.average_salary)
        student_satisfaction = str(course.student_satisfaction)
        course_length = str(course.course_length)
        course_level = str(course.course_level)
        fees = str(course.fees)
        entry_requirements = str(course.entry_requirements)
        university = str(course.course_university)
        employment_rate = str(course.employment_rate)

        # Connect to database
        conn = sqlite3.connect(output_file_arg)
        c = conn.cursor()
        c.execute("INSERT INTO courses (name, university, url, average_salary, student_satisfaction, course_length, course_level, fees, entry_requirements, employment_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, university, url, average_salary, student_satisfaction, course_length, course_level, fees, entry_requirements, employment_rate))
        conn.commit()
        conn.close()
        print("Course inserted")
    def insert_all(courses):
        for course in courses.courses:
            Database.insert(course)

def getListOfCourses():
    print("Getting list of courses")
    # https://www.ucas.com/explore/subjects
    # Get list of courses from UCAS website
    url = "https://www.ucas.com/explore/subjects"
    attempts = 0
    while (True and attempts < 5):
        try:
            response = requests.get(url)
            break
        except Exception as e:
            attempts += 1
            print(e)
            sleep(10)
    soup = bs.BeautifulSoup(response.text, "html.parser")
    # property data-v-56118ceb
    courses = soup.find_all("h3", {"data-v-56118ceb": True})
    # Get the text from the h3 tag
    courses = [course.text for course in courses]
    return courses


# Get system arguments for course and output file
if len(sys.argv) < 3:
    print("Please provide a course and output file")
    exit()
course_arg = sys.argv[1]
output_file_arg = sys.argv[2]

if __name__ == "__main__":
    Database.create()
    for course in getListOfCourses():
        get_course_data(course)

### Explain the above code generally
'''
The above code is a web scraper that scrapes the data from the UCAS website
and stores it in a database called courses.db

The code is split into 4 classes:
    Crawler - This class contains methods that are used to crawl the website
    Course - This class contains the data for a single course
    Courses - This class contains a list of Course objects
    Database - This class contains methods that are used to interact with the database
'''
'''
The class mermaid diagram for the above code is as follows:
classDiagram
    class Crawler{
        +get_soup(url)
        +get_element_list(soup, element)
        +get_data_text(element)
    }
    class Course{
        +name
        +url
        +average_salary
        +student_satisfaction
        +course_length
        +course_level
        +course_university
        +fees
        +entry_requirements
    }
    class Courses{
        +courses
    }
    class Database{
        +create()
        +insert(course)
        +insert_all(courses)
    }
    Course *-- Courses
    Course -- Crawler
    Database -- Courses
    Database -- Course
    
'''
### Explain the above code in detail
'''
The code is split into 4 classes:
    Crawler - This class contains methods that are used to crawl the website
    Course - This class contains the data for a single course
    Courses - This class contains a list of Course objects
    Database - This class contains methods that are used to interact with the database

The Crawler class contains 3 methods:
    get_soup - This method takes a url as an argument and returns the parsed soup
    get_element_list - This method takes a soup and a list of elements to find and returns a list of elements
    get_data_text - This method takes an element and returns the text data

The Course class contains 9 variables:
    name - This variable contains the name of the course
    url - This variable contains the url of the course
    average_salary - This variable contains the average salary after the course
    student_satisfaction - This variable contains the student satisfaction for the course
    course_length - This variable contains the length of the course
    course_level - This variable contains the level of the course
    fees - This variable contains the fees for the course
    entry_requirements - This variable contains the entry requirements for the course
'''
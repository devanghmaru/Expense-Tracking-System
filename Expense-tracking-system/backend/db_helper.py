import mysql.connector
from contextlib import contextmanager
import logging_setup

logger = logging_setup.setup_logging("db_helper")

@contextmanager
def db_connection(commit = False):
    connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "root",
        database = "expense_manager",
    )
    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    cursor.close()
    connection.close()

def fetch_all():
    logger.info("Fetching all expenses")
    with db_connection() as cursor:
        cursor.execute('SELECT * FROM expenses')
        results = cursor.fetchall()
        for row in results:
            print(row)

def fetch_by_date(expense_date):
    logger.info(f"fetch_by_date called with {expense_date}")
    with db_connection() as cursor:
        cursor.execute('SELECT * FROM expenses WHERE expense_date = %s', (expense_date,))
        results = cursor.fetchall()
        return results

def fetch_by_date_range(start_date, end_date):
    logger.info(f"fetch_by_date_range called with {start_date}, {end_date}")
    with db_connection() as cursor:
        cursor.execute(
            """
            SELECT * FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            """,
            (start_date, end_date,)
        )
        results = cursor.fetchall()
        return results

def fetch_expenses_summary(start, end):
    logger.info(f"fetch_expenses_summary called with {start}, {end}")
    with db_connection() as cursor:
        cursor.execute(
            '''SELECT category, sum(amount) as total_amount 
               FROM expenses 
               WHERE expense_date 
               Between %s and %s GROUP BY category''', (start, end)
        )
        results = cursor.fetchall()
        return results

def fetch_available_years():
    logger.info(f"fetch_available_years called")
    with db_connection() as cursor:
        cursor.execute(
            '''
            SELECT DISTINCT YEAR(expense_date) AS year
            FROM expenses
            ORDER BY year;
            '''
        )
        return cursor.fetchall()

def fetch_expenses_by_month(year:str):
    logger.info(f"fetch_expenses_by_month called with year: {year}")
    with db_connection() as cursor:
        cursor.execute(
            '''SELECT 
                    DATE_FORMAT(expense_date, '%M-%Y') AS month,
                    SUM(amount) AS total_amount
                FROM expenses
                WHERE YEAR(expense_date) = %s
                GROUP BY month
                ORDER BY MIN(expense_date);
            ''',(year,)
        )
        results = cursor.fetchall()
        return results

def insert_one(expense_date,amount,category,notes):
    logger.info(f"insert_one called with {expense_date}, {amount}, {category}, {notes}")
    with db_connection(commit=True) as cursor:
        cursor.execute(
            'INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)',
            (expense_date, amount, category, notes)
        )

def delete_one(expense_date):
    logger.info(f"delete_one called with {expense_date}")
    with db_connection(commit=True) as cursor:
        cursor.execute(
            'DELETE FROM expenses WHERE expense_date = %s', (expense_date,)
        )

if __name__ == '__main__':
    result = fetch_by_date_range("2024-01-01","2024-12-31")
    for row in result:
        print(row)

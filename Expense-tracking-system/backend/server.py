from datetime import date
from typing import List
import uvicorn
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import db_helper

class Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start: date
    end: date

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/expenses/{expense_date}", response_model = List[Expense])
def get_expenses(expense_date: date):
    expense = db_helper.fetch_by_date(expense_date)
    if expense is None:
        raise HTTPException(status_code=404, detail="No data found")
    return expense

@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expense: List[Expense]):
    db_helper.delete_one(expense_date)
    for expense in expense:
        db_helper.insert_one(expense_date, expense.amount, expense.category, expense.notes)
    return {"message": "Expense Update successfully"}

@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expenses_summary(date_range.start, date_range.end)

    if data is None:
        raise HTTPException(status_code=404, detail="No data found")

    total = sum([row['total_amount'] for row in data])

    breakdown = {}
    for row in data:
        percentage = (row['total_amount'] / total) * 100 if total != 0 else 0
        breakdown[row['category']] = {
            'total_amount': row['total_amount'],
            'percentage': percentage,
        }
    return breakdown

@app.get("/expenses/")
async def get_expenses(date_range: DateRange):
    data = db_helper.fetch_by_date_range(date_range.start, date_range.end)
    if data is None:
        raise HTTPException(status_code=404, detail="No data found")

    return data

@app.get("/analytics/years")
def get_available_years():
    years = db_helper.fetch_available_years()
    return [{'year': str(row['year'])} for row in years]

@app.get("/analytics/month")
def get_analytics_by_month(year: str):
    data = db_helper.fetch_expenses_by_month(year)
    breakdown = []
    for row in data:
        breakdown.append({
            'month': row['month'],
            'total_amount': row['total_amount'],
        })
    return breakdown

if __name__ == "__main__":
    uvicorn.run(app)
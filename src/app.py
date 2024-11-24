import altair as alt
import pandas as pd

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .application import Application 
from .repositories import SQLiteTransactionRepository

app = FastAPI()

# Initialize SQLite repository
sqlite_repo = SQLiteTransactionRepository("transactions.db")

# Create the application
sql_app = Application(sqlite_repo)

# Mount static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/add-transaction", response_class=HTMLResponse)
async def add_transaction_form(request: Request):
    return templates.TemplateResponse("transaction_form.html", {"request": request})

@app.get('/update-transaction', response_class=HTMLResponse)
async def update_transaction_form(request: Request):
    return templates.TemplateResponse('transaction_update_form.html', {'request': request})

@app.post("/add-transaction", response_class=HTMLResponse)
async def handle_transaction(
    request: Request,
    amount: float = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    notes: str = Form(None)
):

    sql_app.create_transaction(amount, date, description, category, notes)

    return templates.TemplateResponse(
        "transaction_form.html",  # Ensure this template exists
        {"request": request}
    )

@app.get('/get-last-seven-days', response_class=HTMLResponse)
async def get_last_seven_days(request: Request):

    # Use sql app to correct transaction
    transactions = sql_app.list_last_seven_days()

    # Convert to dataframe
    df = pd.DataFrame([vars(obj) for obj in transactions])

    # Filter df to only purchases
    df.amount = df.amount * -1
    df = df.groupby('category').sum().reset_index()
    print(df)

    # Build a chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('category:N', title='Category'),
        y=alt.Y('amount:Q', title='Amount'),
    ).properties(
        width=800
    )

    return templates.TemplateResponse(
        'transactions_last_seven.html', 
        {
            'request': request,
            'transactions': transactions,
            'chart_json': chart.to_json()
        }
    )
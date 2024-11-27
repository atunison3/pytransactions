import altair as alt
import pandas as pd

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional

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
    # Get current budget categories
    categories = sql_app.list_categories()
    success_message = request.query_params.get("success")

    return templates.TemplateResponse(
        "transaction_form.html", 
        {
            "request": request,
            'categories': categories,
            'success_message': "Transactions submitted successfully!" if success_message else None
        })

@app.get('/update-transaction', response_class=HTMLResponse)
async def update_transaction_form(request: Request):
    return templates.TemplateResponse('transaction_update_form.html', {'request': request})

@app.get('/add-batch-transaction', response_class=HTMLResponse)
async def add_batch_transaction(request: Request):
    # Get the current categories
    categories = sql_app.list_categories()

    return templates.TemplateResponse(
        'multi_transaction_form.html',
        {
            'request': request,
            'categories': categories
        }
    )
   
@app.post('/submit-itemized-transaction', response_class=HTMLResponse)
async def process_itemized_transaction(
    request: Request, 
    date: str = Form(...),
    descriptions: list[str] = Form(...),
    amounts: list[float] = Form(...),
    categories: list[str] = Form(...),
    notes: list[str] = Form(None)
    ):
    for i in range(len(notes)):
        #sql_app.create_transaction(amount, date, description, category, notes)
        sql_app.create_transaction(amounts[i], date, descriptions[i], categories[i], notes[i])

    return RedirectResponse(url="/add-batch-transaction?success=true", status_code=303)


@app.get('/add-category', response_class=HTMLResponse)
async def add_category_form(request: Request):
    # Get current category data 
    categories = sql_app.list_categories()

    # Build df
    df = pd.DataFrame([vars(obj) for obj in categories])

    # Chart it
    chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y('description', title='Category'),
        x=alt.X('monthly_allocation', title='Monthly Allocation')
    ).properties(
        title='Current Categories',
        width=600
    )

    return templates.TemplateResponse(
        'category_form.html', 
        {
            'request': request,
            'chart_json': chart.to_json(),
            'categories': categories
        })

@app.get('/get-last-seven-days', response_class=HTMLResponse)
async def get_last_seven_days(request: Request):

    # Use sql app to correct transaction
    transactions = sql_app.list_last_seven_days()

    # Convert to dataframe
    df = pd.DataFrame([vars(obj) for obj in transactions])

    # Filter df to only purchases
    df.amount = df.amount * -1
    df = df.groupby('category').sum().reset_index()

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

@app.get('/get-current-month', response_class=HTMLResponse)
async def get_current_month(request: Request):
    # Get this months transactions
    transactions = sql_app.list_current_month()

    # Convert to dataframe
    transactions_df = pd.DataFrame([vars(obj) for obj in transactions])

    # Filter df to only purchases
    transactions_df.amount = transactions_df.amount * -1
    transactions_df = transactions_df.groupby('category').sum().reset_index()
    transactions_df['color'] = ['Spent'] * len(transactions_df)

    # Merge with categories
    categories = sql_app.list_categories()
    categories_df = pd.DataFrame([vars(obj) for obj in categories])
    categories_df['color'] = ['Allowance'] * len(categories_df)
    df = transactions_df.merge(categories_df, left_on='category', right_on='description')
    df = df[['category', 'amount', 'monthly_allocation']]

    # Melt df
    df = pd.melt(df, id_vars=['category'], value_vars=['amount', 'monthly_allocation'])

    # Filter to only expenses
    df = df[(df['category'] != 'Income') & (df['category'] != 'Investment')]

    # Build a chart
    chart = alt.Chart(df).mark_bar(opacity=0.5).encode(
        y=alt.Y('category:N', title='Category'),
        x=alt.X('value:Q', title='Amount   [$ USD]').stack(None),
        color=alt.Color('variable:N', title=None)
    )

    return templates.TemplateResponse(
        'transactions_this_month.html', 
        {
            'request': request,
            'transactions': transactions,
            'chart_json': chart.to_json()
        }
    )

@app.get('/get-recurring-expense', response_class=HTMLResponse)
async def get_recurring_expenses(request: Request):

    # Get all recurring expenses
    recurring_expenses = sql_app.list_all_recurring()

    return templates.TemplateResponse(
        'recurring_expenses.html',
        {
            'request': request,
            'recurring_expenses': recurring_expenses
        }
    )

@app.post('/add-category', response_class=HTMLResponse)
async def add_budet_category(
    request: Request,
    monthly_allocation: float = Form(...),
    description: str = Form(...),
    notes: str = Form(...)
    ):

    sql_app.create_category(description, monthly_allocation, notes)

    # Get current category data 
    categories = sql_app.list_categories()

    # Build df
    df = pd.DataFrame([vars(obj) for obj in categories])

    # Chart it
    chart = alt.Chart(df).mark_bar().encode(
        y=alt.Y('description', title='Category'),
        x=alt.X('monthly_allocation', title='Monthly Allocation')
    ).properties(
        title='Current Categories',
        width=600
    )

    return templates.TemplateResponse(
        'category_form.html',
        {
            'request': request,
            'chart_json': chart.to_json()
        }
    )

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

    # Get current budget categories
    categories = sql_app.list_categories()

    return templates.TemplateResponse(
        "transaction_form.html",  # Ensure this template exists
        {
            "request": request,
            'categories': categories
        }
    )

@app.post('/update-transaction', response_class=HTMLResponse)
async def update_transaction(
    request: Request, 
    transaction_id: int = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    notes: str = Form(None)
    ):
    sql_app.correct_transaction(
        transaction_id, amount, 
        date, description, 
        category, notes
    )

    # Get current budget categories
    categories = sql_app.list_categories()

    return templates.TemplateResponse(
        'transaction_form.html', 
        {
            'request': request,
            'categories': categories
        }
    )

@app.post('/add_recurring_expense', response_class=HTMLResponse)
async def handle_recurring_expense(
    request: Request, 
    amount: int = Form(...),
    frequency: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    notes: str = Form(None)
):
    try:
        sql_app.create_recurring_expense(amount, frequency, category, description, notes)
        status_statement = f'Successfully added {description} recurring expense!'
        status_color = 'green'
    except Exception as e:
        status_statement = f'Failed to add recurring expense: {e}'
        status_color = 'red'

    

    return templates.TemplateResponse(
        'recurring_expenses.html',
        {
            'request': request,
            'status_statement': status_statement,
            'status_color': status_color
        }
    )

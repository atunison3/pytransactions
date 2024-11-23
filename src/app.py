#import altair as alt
#import pandas as pd

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

    # Use sql app to correct transaction
    sql_app.correct_transaction(
        transaction_id, amount, 
        date, description, 
        category, notes
    )

    return templates.TemplateResponse(
        'transaction_update_form.html', 
        {'request': request}
    )
from fastapi import FastAPI, HTTPException
import psycopg2

app = FastAPI()

# Подключение к базе данных
conn = psycopg2.connect(
    host="127.0.0.1",
    database="postgres",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

@app.get("/convert")
async def convert_currency(currency_name: str, amount: float):
    # Проверка, есть ли такая валюта в базе
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    currency = cur.fetchone()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    # Получение курса валюты
    rate = currency[2]

    # Конвертация
    converted_amount = amount * rate

    return {"converted_amount": converted_amount}

@app.get("/currencies")
async def get_currencies():
    # Получение списка всех валют
    cur.execute("SELECT * FROM currencies")
    currencies = cur.fetchall()

    # Формирование ответа в виде списка строк
    currencies_list = []
    for currency in currencies:
        currencies_list.append(f"{currency[1]}: {currency[2]}")

    return {"currencies": currencies_list}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)

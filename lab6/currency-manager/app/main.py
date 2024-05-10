from fastapi import FastAPI, HTTPException, Request
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

@app.post("/load")
async def load_currency(request: Request):
    data = await request.json()
    currency_name = data.get("currency_name")
    rate = data.get("rate")

    # Проверка, есть ли уже такая валюта в базе
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Currency already exists")

    # Сохранение валюты в таблицу
    cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (currency_name, rate))
    conn.commit()

    return {"message": "Успешно сохраненная валюта"}

@app.post("/update_currency")
async def update_currency(request: Request):
    data = await request.json()
    currency_name = data.get("currency_name")
    new_rate = data.get("new_rate")

    # Проверка, есть ли такая валюта в базе
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Currency not found")

    # Обновление курса валюты
    cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (new_rate, currency_name))
    conn.commit()

    return {"message": "Валюта успешно обновлена"}

@app.post("/delete")
async def delete_currency(request: Request):
    data = await request.json()
    currency_name = data.get("currency_name")

    # Проверка, есть ли такая валюта в базе
    cur.execute("SELECT * FROM currencies WHERE currency_name = %s", (currency_name,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Currency not found")

    # Удаление валюты из таблицы
    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
    conn.commit()

    return {"message": "Валюта успешно удалена"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
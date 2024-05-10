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
conn.commit()

# Получение роли пользователя (администратора)
@app.get("/get_admin/{chat_id}")
async def get_admin(chat_id: str):
    # Получение роли пользователя
    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (chat_id,))
    admin = cur.fetchone()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"admin": admin[1]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)



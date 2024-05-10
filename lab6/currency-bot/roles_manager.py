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

# Добавление роли пользователю (администратора)
@app.post("/add_admin/{chat_id}")
async def add_admin(chat_id: str):
    # Проверка, есть ли уже такая роль у пользователя
    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (chat_id,))
    existing_admin = cur.fetchone()
    if existing_admin:
        raise HTTPException(status_code=400, detail="User already has a role")

    # Добавление роли
    cur.execute("INSERT INTO admins (chat_id) VALUES (%s)", (chat_id,))
    conn.commit()

    return {"message": "Admin added successfully"}

# Получение роли пользователя (администратора)
@app.get("/get_admin/{chat_id}")
async def get_admin(chat_id: str):
    # Получение роли пользователя
    cur.execute("SELECT * FROM admins WHERE chat_id = %s", (chat_id,))
    admin = cur.fetchone()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"admin": admin[1]}

# Удаление роли пользователя (администратора)
@app.delete("/delete_admin/{chat_id}")
async def delete_admin(chat_id: str):
    # Удаление роли пользователя
    cur.execute("DELETE FROM admins WHERE chat_id = %s", (chat_id,))
    conn.commit()

    return {"message": "Admin deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)



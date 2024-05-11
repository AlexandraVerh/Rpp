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
    admin = cur.fetchone()#Получаем первую строку результата запроса.
    # Если строки не существует (значение admin будет None), то генерируется HTTPException с кодом состояния 404
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return {"admin": admin[1]}#Если информация о пользователе найдена, возвращается словарь с ключом "admin",
    # содержащим второй элемент кортежа admin, предположительно представляющий роль пользователя.

if __name__ == "__main__":
    import uvicorn#предоставляет ASGI сервер для запуска FastAPI приложений.
    uvicorn.run(app, host="0.0.0.0", port=5003)
#выводит приложение FastAPI с помощью сервера uvicorn.
# Параметр app - это ваше FastAPI приложение, а host="0.0.0.0" и port=5003 определяют хост и порт, на которых будет запущен сервер.


from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Настройка кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 3600})

# Настройка лимитирования запросов
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per hour"]
)

# Статические данные о погоде
weather_data = {
    "Moscow": {"temperature": "5°C", "condition": "Облачно"},
    "New York": {"temperature": "10°C", "condition": "Солнечно"},
    # Добавьте другие города по необходимости
}

@app.route('/weather/<city>', methods=['GET'])
@cache.cached(timeout=3600)
@limiter.limit("10 per hour")
def get_weather(city):
    if city in weather_data:
        return jsonify(weather_data[city])
    else:
        return jsonify({"error": "Город не найден"}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Превышен лимит ставок", "retry_after": e.description}), 429

if __name__ == '__main__':
    app.run(debug=True)


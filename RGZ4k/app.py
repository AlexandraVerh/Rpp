from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

app = Flask(__name__)

# Настройки кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Настройки ограничения частоты запросов
limiter = Limiter(
    get_remote_address,
    default_limits=["10 per hour"]
)

# Статические данные о погоде
weather_data = {
    "Moscow": {"temperature": -5, "condition": "Снег"},
    "New York": {"temperature": 3, "condition": "Дождь"},
    "Tokyo": {"temperature": 10, "condition": "Ясно"},
}


@app.route('/weather/', methods=['GET'])
@limiter.limit("10 per hour")
@cache.cached(timeout=3600, query_string=True)
def get_weather():
    city = request.args.get('city')
    if city not in weather_data:
        return jsonify({"error": "Город не найден"}), 404

    return jsonify(weather_data[city])


if __name__ == '__main__':
    app.run(debug=True)

import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os



class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'database.db')
        conn = sqlite3.connect(DATABASE_PATH)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
    # Приводим к нормальному виду, чтобы избежать проблем с регистром
        city_name = city_name.strip().title()  # Преобразуем, например, "tokyo" в "Tokyo"
    
        print(f"Поиск координат для города: {city_name}")  # Логирование для отладки

        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                         FROM cities
                         WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
        
        if coordinates:
            print(f"Координаты для {city_name}: {coordinates}")  # Логируем успешный результат
            return coordinates
        else:
            print(f"Город {city_name} не найден в базе.")  # Логируем ошибку
            return None





    def create_grapf(self, path, cities):
    # Создаем карту
        ax = plt.axes(projection=ccrs.Mollweide())
        ax.stock_img()
    
    # Добавляем города на карту
        for city, (lat, lon) in cities.items():  # Используем .items() для словаря
        # Получаем координаты города
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lon = coordinates
                ax.plot(lon, lat, marker='o', color='red', markersize=8, transform=ccrs.PlateCarree())  # Точка города
                ax.text(lon + 3, lat + 3, city, fontsize=12, horizontalalignment='left', transform=ccrs.PlateCarree())  # Текст города

        if os.path.exists(path):
            os.remove(path)  # Удаляем старую картинку, если она существует
    # Сохраняем изображение
        plt.savefig(path)
        plt.close()
    # Обновленный метод draw_distance в классе DB_Map
    def draw_distance(self, city1, city2, path):
    # Получаем координаты двух городов
        coordinates1 = self.get_coordinates(city1)
        coordinates2 = self.get_coordinates(city2)

        if not coordinates1 or not coordinates2:
            return  # Если координаты хотя бы одного города не найдены

        lat1, lon1 = coordinates1
        lat2, lon2 = coordinates2

        # Создаем карту
        ax = plt.axes(projection=ccrs.Mollweide())
        ax.stock_img()

        # Рисуем линию между двумя городами
        ax.plot([lon1, lon2], [lat1, lat2], color='red', marker='o', transform=ccrs.Geodetic())

        # Добавляем названия городов на точки
        ax.text(lon1, lat1, city1, transform=ccrs.Geodetic(), color='black', fontsize=10, ha='right', va='top')
        ax.text(lon2, lat2, city2, transform=ccrs.Geodetic(), color='black', fontsize=10, ha='left', va='bottom')
        
        # Проверяем, существует ли файл, и удаляем его перед созданием нового
        if os.path.exists(path):
            os.remove(path)  # Удаляем старую картинку, если она существует
    # Сохраняем изображение в файл
        plt.savefig(path)
        plt.close()



if __name__ == "__main__":
    from config import DATABASE  # Импортируем переменную DATABASE из конфигурационного файла
    
    m = DB_Map(DATABASE)  # Передаем переменную DATABASE при создании объекта
    m.create_user_table()  # Вызов метода

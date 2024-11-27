import os
import json
import sqlite3


class PriceMachine():

    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0

    def load_prices(self, file_path=''):
        '''
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт
                
            Допустимые названия для столбца с ценой:
                розница
                цена
                
            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        '''
        #        con1 = sqlite3.connect("bd.db")
        #        cursor1 = con1.cursor()
        # Нахождение файлов содержащих слово price
        #        print(os.listdir(file_path))
        true_files = []
        for true_file in os.listdir(file_path):
            if 'price' in true_file:
                true_files.append(true_file)
        #        print(true_files)

        # Нахождение номеров столбцов
        for file1 in true_files:
            with open('data/' + file1, 'r', encoding='utf-8') as f:
                headers = f.readline()
                number_columns = self._search_product_price_weight(headers)
                #                print(number_columns)
                for line in f:
                    line_list = line.split(',')
                    #                    print(line_list)
                    #                    print(line_list[number_columns.get('tovar')], line_list[number_columns.get('price')], line_list[number_columns.get('weight')])
                    # Заполнение БД
                    cost_by_weigth = round(
                        int(line_list[number_columns.get('price')]) / int(line_list[number_columns.get('weight')]), 2)
                    cursor.execute(
                        " INSERT INTO Tovary_BD (tovar, price, file, weigth, cost_by_weigth) VALUES (?,?,?,?,?)",
                        (line_list[number_columns.get('tovar')],
                         line_list[number_columns.get('price')],
                         file1,
                         line_list[number_columns.get('weight')],
                         cost_by_weigth))

                    con.commit()

    #        con1.close()

    def _search_product_price_weight(self, headers=''):
        '''
            Возвращает номера столбцов
        '''
        tovar = ['товар', 'название', 'наименование', 'продукт']
        price = ['розница', 'цена']
        weight = ['вес', 'масса', 'фасовка']
        headers = headers.rstrip('\n')
        headers_list = headers.split(',')
        #        print(headers_list)
        i = 0
        number_columns = {}
        for line in headers_list:
            if line in tovar:
                number_columns.update({'tovar': i})
            if line in price:
                number_columns.update({'price': i})
            if line in weight:
                number_columns.update({'weight': i})
            i += 1
        return number_columns

    def export_to_html(self, fname='output.html'):

        cursor.execute(
            f"SELECT * FROM Tovary_BD ORDER BY cost_by_weigth")
        tovars = cursor.fetchall()
        result = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title> Позиции продуктов </title>
        </head>
        <body>
            <table border="1">
                <thead>
                  <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                  </tr>
                </thead>
                <tbody>
        '''
        d = 1
        for tovar in tovars:
            result += f'<tr>'
            result += f' <td align="center"> {d} </td> '
            result += f'<td > {tovar[1]} </td>'
            result += f'<td align="center"> {tovar[2]} </td>'
            result += f'<td align="center"> {tovar[4]} </td>'
            result += f'<td align="center"> {tovar[3]} </td>'
            result += f'<td align="right"> {tovar[5]} </td>'
            result += f'<tr>'
            d += 1

        result += '''
                </tbody>
            </table>     
        </body>
        '''
        with open('data/' + fname, 'w', encoding='utf-8') as f:
            f.write(result)
        return result

    def find_text(self, text1):
        cursor.execute(
            f"SELECT tovar, price, weigth, file , cost_by_weigth  FROM Tovary_BD WHERE tovar LIKE '%{text1}%' ORDER BY cost_by_weigth")
        tovars = cursor.fetchall()
        print('№'.center(4) + 'Наименование'.center(26) + 'цена'.center(8) + 'вес(кг)'.center(9) + 'фаил'.center(
            18) + 'цена за кг.'.center(15))
        d = 1
        for tovar in tovars:
            print(str(d).center(4), tovar[0].ljust(26), str(tovar[1]).ljust(8), str(tovar[2]).ljust(9),
                  tovar[3].ljust(18), str(tovar[4]).ljust(15))
            d += 1


pm = PriceMachine()
# Создание таблицы товаров в базе данных
con = sqlite3.connect("bd.db")
cursor = con.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS Tovary_BD
                                    (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                                    tovar TEXT, 
                                    price INTEGER,
                                    file TEXT,
                                    weigth INTEGER,
                                    cost_by_weigth INTEGER)
                                """)
cursor.execute("DELETE FROM Tovary_BD")
con.commit()
print("Производится выборкадынных из приайсов, это может занять какое то время")

print(pm.load_prices('data'))
'''
    Логика работы программы
'''
text1 = ''

while text1 != 'exit':
    text1 = input('Введите текст для поиска, или "exit" для завершения работы: ')
    pm.find_text(text1)

'''
    Логика работы программы
'''
print('the end')

print(pm.export_to_html())
con.close()

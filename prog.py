import csv
import datetime as dt
import time

# TODO исправить вычисление времени прилета, т.к. работает некорректно при времени перелета около 24.00, т.к. дата
# прилета меняется на следующее число, а программа это не обрабатывает


class RevTree(object):
    """Класс для хранения цепочки перелетов и удобного их считывания
    Корневой элемент должен иметь данные типа None"""
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

    def __len__(self):
        """Возвращает количество узлов в ветви"""
        # TODO переделать возвращаемую длину на -1, если последний элемент равен "end"
        length = 0
        if self.parent is None:
            length = 1
        else:
            length = 1
            copy = self
            while copy.parent is not None:
                copy = copy.parent
                length += 1
        return length


def is_destination(destination, flight):
    """destination - IATA-код конечного аэропорта
    flight - полная информация о рейсе
    Функция регистрозависимая"""
    # flight[17] - IATA-код аэропорта назначения текущего рейса
    if str(destination) == str(flight[17]):
        return True
    else:
        return False


def do_one_iter(data, previous_flight, already_been, point_dest):
    """previous_flight - тип: RevTree. Хранит информация о вершине, т.е. как мы прилетели в данный аэропорт"""

    paths = list()  # маршруты, которые привели к точке назначения
    possible_flights = list()  # возможные рейсы из данного аэропорта
    previous_flight_list = previous_flight.data
    current_point = previous_flight_list[17]  # куда мы прилетели
    arrival_date_time = dt.datetime(int(previous_flight_list[0]), int(previous_flight_list[1]),\
                                    int(previous_flight_list[2]), int(previous_flight_list[6][:-2]),\
                                    int(previous_flight_list[6][-2:]))
    temp = list()  # хранит полеты только из данного аэропорта
    for row in data:
        # ищем маршруты из текущего аэропорта на заданное число, так, чтобы не попасть в аэропорты в коротые
        # мы прибыли на других шагах
        # странное и непонятное время, пока будем просто удалять "битые" записи
        if str(row[0]) == "" or str(row[1]) == "" or str(row[2]) == "" or  \
                str(row[6][:-2]) == "" or str(row[6][-2:]) == "":
            print(row)
            continue
        try:
            row_date_time = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(row[6][:-2]), int(row[6][-2:]))
        except ValueError:
            if int(row[6][:-2]) == 24:
                row_date_time = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(0), int(row[6][-2:]))
        if str(row[16]) == str(current_point) and arrival_date_time < row_date_time and row[17] not in already_been:
            temp.append(row)
    # -------------------------------------------------------------------
    # print("Рейсов из " + str(previousFlightList[17]) + " найдено: " + str(len(temp)))
    # input()
    # print("Найденные рейсы из " + str(previousFlightList[17]))
    # for row in temp:
    # print(row)
    # input()
    # -------------------------------------------------------------------
    if len(temp) == 0:  # если исходящих рейсов из данного аэропорта нет, то помечаем это путь как завершенный
        possible_flights.append(RevTree(previous_flight, "end"))
    else:
        while len(temp) > 0:
            current_flight = temp[0]
            del temp[0]
            # если в списке полетов мы остался один рейс, которого нет у нас, то добавляем его у возможные пути
            if len(temp) == 0:
                possible_flights.append(RevTree(previous_flight, current_flight))
                # проверяем, не прилетели ли мы уже в нужный аэропорт
                if is_destination(point_dest, current_flight):
                    paths.append(RevTree(None, current_flight))
                break

            current_arrival_date_time = dt.datetime(int(current_flight[0]), int(current_flight[1]),\
                                                    int(current_flight[2]), int(current_flight[6][:-2]),\
                                                    int(current_flight[6][-2:]))

            i = 0
            while i < len(temp):
                # 6-й элемент - время прибытия рейса
                # 21 и 23 - метки отмены рейса
                # if elem[17] == currentFlight[17] and compare_time(elem[6], currentFlight[6]) == -1:
                elem_arrival_date_time = dt.datetime(int(temp[i][0]), int(temp[i][1]), int(temp[i][2]), int(temp[i][6][:-2]), int(temp[i][6][-2:]))
                if temp[i][17] == current_flight[17] and current_arrival_date_time > elem_arrival_date_time:
                    current_flight = temp[i]
                    del temp[i]
                    current_arrival_date_time = dt.datetime(int(current_flight[0]), int(current_flight[1]), int(current_flight[2]), int(current_flight[6][:-2]), int(current_flight[6][-2:]))
                elif temp[i][17] == current_flight[17] and current_arrival_date_time <= elem_arrival_date_time:
                    del temp[i]
                else:
                    i += 1
            # проверяем, не прилетели ли мы уже в нужный аэропорт
            if is_destination(point_dest, current_flight):
                paths.append(RevTree(previous_flight, current_flight))
            # заполняем список маршрутами из текущего аэропорта
            possible_flights.append(RevTree(previous_flight, current_flight))
    return paths, possible_flights


def find_path(data_input, date, point_orig, point_dest):
    # data - список всех полетов за год в виде datetime
    # date - дата полета в виде datetime
    # point_orig - IATA код аэропорта прибытия
    # point_dest - IATA код аэропорта назначения
    # Когда мы запускаем эту функцию, мы знаем из какого аэропорта, куда, и какого числа летим
    # Находим минимальный по кол-ву пересадок маршрут. и возвращаем его в виде списка с информацией о полете(ах)
    data = data_input
    paths = list()  # Найденные пути до пункта назначения
    already_been = set()  # IATA-коды аэропортов, из которых мы уже вылетали на предыдущих шагах
    already_been.add(point_orig)
    possible_flights = list()  # возможные маршруты из конкретной точки
    is_done = False
    # 1. Убираем из поиска все полеты, которые были до введенной даты, они нас не интересуют
    print("Передано маршрутов в функцию " + str(len(data)))
    # for row in data:
    # 	if int(row[1]) >= int(date[1]):
    # 		if int(row[2]) >= int(date[2]):
    # 			possibleFlights.append(row)
    # data = possibleFlights
    # print("Данные которые нам нужны, т.е. после введенной даты: " + str(len(data)))

    current_flight = list()  # информация о конкретном полете
    temp = list()  # временная
    k = 0
    while not is_done:
        first_move = False  # флаг для первого действия
        if not first_move:
            for row in data:
                # ищем маршруты из пункта отправки на заданное число, так,
                # чтобы не попасть в аэропорты в коротые мы прибыли на других шагах
                if str(row[16]) == str(point_orig) and int(date.month) == int(row[1]) and int(date.day) == int(row[2]):
                    temp.append(row)
                    data.remove(row)
            # print("Вылетело из первого аэропора сегодня: " + str(len(temp)))
            # input()

            # ищем возможные рейсы из начального аэропорта
            while len(temp) > 0:
                current_flight = temp[0]
                del temp[0]
                # если в списке полетов мы остался один рейс, которого нет у нас, то добавляем его у возможные пути
                if len(temp) == 0:
                    possible_flights.append(RevTree(None, current_flight))
                    # проверяем, не прилетели ли мы уже в нужный аэропорт
                    if is_destination(point_dest, current_flight):
                        paths.append(RevTree(None, current_flight))
                        print("Добавили в найденные пути:")
                        print(current_flight)
                        # input()
                    break

                current_arrival_date_time = dt.datetime(int(current_flight[0]), int(current_flight[1]),\
                                                        int(current_flight[2]), int(current_flight[6][:-2]),\
                                                        int(current_flight[6][-2:]))
                #
                # ниже логический цикл "for" оформлен как "while", для правильной итерации
                i = 0
                while i < len(temp):
                    # 6-й элемент - время прибытия рейса
                    # 21 и 23 - метки отмены рейса
                    # if elem[17] == currentFlight[17] and compare_time(elem[6], currentFlight[6]) == -1:
                    elem_arrival_date_time = dt.datetime(int(temp[i][0]), int(temp[i][1]), int(temp[i][2]),\
                                                         int(temp[i][6][:-2]), int(temp[i][6][-2:]))
                    if temp[i][17] == current_flight[17] and current_arrival_date_time > elem_arrival_date_time:
                        current_flight = list(temp[i])
                        current_arrival_date_time = dt.datetime(int(current_flight[0]), int(current_flight[1]),\
                                                                int(current_flight[2]), int(current_flight[6][:-2]),\
                                                                int(current_flight[6][-2:]))
                        del temp[i]
                    elif temp[i][17] == current_flight[17] and current_arrival_date_time <= elem_arrival_date_time:
                        del temp[i]
                    else:
                        i += 1
                # проверяем, не прилетели ли мы уже в нужный аэропорт
                if is_destination(point_dest, current_flight):
                    paths.append(RevTree(None, current_flight))
                    print("Добавили в найденные пути:")
                    print(current_flight)
                    input()
                # заполняем список маршрутами из стартового аэропорта
                possible_flights.append(RevTree(None, current_flight))
            # -------------------------------------------------------------------
            # print("Возможные пути на первом шаге:")
            # for each in possibleFlights:
            # 	print(str(each.parent) + " " + str(each.data))
            # -------------------------------------------------------------------
            # добавляем аэропорты, из которых мы уже вылетали, чтобы не проходить их заново
            # currentFlight[16] - IATA-код аэропорта отправления рейса
            already_been.add(current_flight[16])
            # dataToWrite = list()
            # for row in possibleFlights:
            # 	dataToWrite.append(row.data)
            # write_csv(dataToWrite)
            print("найденный путь:")
            for elem in paths:
                print(elem.data)
            print(str(len(data)) + " " + str(len(possible_flights)))
            first_move = True
        while len(data) > 0:
            current_detected_paths = list()  # обнаруженные пути из данной вершины до конечной точки назначения
            current_possible_paths = list()  # все найденные пути из данной вершины
            stored_paths = list()          # все найденные пути до точки назначения от данной вершины на текущей глубине
            stored_possible_paths = list()   # все найденные пути из аэропортов на текущей глубине
            stored_already_been = list()     # аэропорты, из которых мы прилетели на текущей глубине
            for elem in possible_flights:
                if elem.data != "end":
                    current_detected_paths, current_possible_paths = do_one_iter(data, elem, already_been, point_dest)
                    # отладка
                    # -------------------------------------------------------------------
                    # print("ИЗ: " + str(elem.data[17]) + " вылетают в " + str(len(elemPossiblePaths)) + " аэропортов")
                    # for each in elemPossiblePaths:
                    # 	print(each.data)
                    # input()
                    # -------------------------------------------------------------------
                    stored_paths.extend(current_detected_paths)
                    stored_possible_paths.extend(current_possible_paths)
                else:
                    continue
            # сначала добавляем в пройденные аэропорты те, которые достигли на предыдущем шаге, чтобы меньше обходить
            for elem in possible_flights:
                if elem.data != "end":
                    if str(elem.data[17]) not in already_been:
                        already_been.add(str(elem.data[17]))
                else:
                    continue
            # возможные пути должны добавляться только после обхода всех аэропортов из PossibleFlights
            possible_flights = stored_possible_paths
            paths.extend(stored_paths)

            i = 0
            while i < len(data):
                if str(data[i][17]) in already_been:
                    del data[i]
                else:
                    i += 1
            if k == len(data):
                is_done = True
                break
            k = len(data)
            print(str(len(data)) + " " + str(len(possible_flights)))
            value_for_debug_point = 10
        is_done = True
    # return possibleFlights
    return paths


def read_file(file_name, date_initial, date_final):
    data = list()
    # data = pd.read_csv(fileName)
    # df = pd.concat(data, ignore_index=True)
    with open(file_name, "r", newline="") as file:
        reader = csv.reader(file)
        reader.__next__()  # пропустили строку с названиями столбцов
        for row in reader:
            copy = row
            # если время прилета битое, пропускаем
            if str(row[0]) == "" or str(row[1]) == "" or str(row[2]) == "" or \
                    str(row[6][:-2]) == "" or str(row[6][-2:]) == "":
                    continue
            # если месяц тот же и дата больше или равна, тогда добавляем
            # 21 и 23 - метки отмены рейса
            # для правильной обработки времени, меняем 24.00 текущей даты, на 00.00 следующего дня
            if int(copy[6][:-2]) == 24 and int(copy[6][-2:]) == 00:
                copy[6] = "0000"
                delta = dt.timedelta(1)
                copy_date = dt.datetime(int(copy[0]), int(copy[1]), int(copy[2])) + delta
                copy[0], copy[1], copy[2] = copy_date.year, copy_date.month, copy_date.day
            else:
                copy_date = dt.datetime(int(copy[0]), int(copy[1]), int(copy[2]))
            if date_initial <= copy_date < date_final and (int(copy[21]) != 1 and int(copy[23]) != 1):
                data.append(copy)
    return data


def compare_time(time1, time2):
    """Время в виде HHMM
    возвращает 1, если time1 > time2
    возвращает 0, если time1 = time2
    возвращает -1, если time1 < time2"""
    result = None
    time1 = list([time1[:-2],time1[-2:]])
    time2 = list([time2[:-2],time2[-2:]])
    if int(time1[0]) > int(time2[0]): result = 1
    if int(time1[0]) < int(time2[0]): result = -1
    if int(time1[0]) == int(time2[0]):
        if int(time1[1]) == int(time2[1]): result = 0
        elif int(time1[1]) > int(time2[1]): result = 1
        elif int(time1[1]) < int(time2[1]): result = -1
    return result


def get_date_final(date_initial):
    """dateInitial имеет тип datetime
    Возвращает дату большую на 2 дня в том же формате
    """
    timedelta = dt.timedelta(2)  # временной отрезок - 2 дня
    date_final = date_initial + timedelta
    return date_final

def get_date_from_row(row):
    """Возвращает DateTime по информации о рейсе"""
    try:
        date = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(row[6][:-2]), int(row[6][-2:]))
        return date
    except IndexError:
        return None


def write_csv(data):
    with open("output.csv", "w", newline="") as file:
        writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for elem in data:
            writer.writerows(elem)
            writer.writerow(" ")  # разделяем пути пустой строкой
    pass


def get_optimal_path(paths, one_or_all):
    """возвращает лучший(ие) маршрут(ы) по длине, если их много, то сортирует по времени
    paths - list of class RevTree, найденные пути
    one_or_many - int, 1 - вернуть лучший маршрут. 2 - вернуть все самые короткие маршруты."""
    # сортируем списки по количеству пересадок
    paths.sort(key=lambda elem: len(elem))
    # т.к. отсортировали по длине, первый элемент имеет наименьшую длину
    min_length = len(paths[0])
    min_paths = list()
    for elem in paths:
        # single_path - последовательность перелетов от начальной до конечной точки
        single_path = list()
        if len(elem) == min_length:
            while elem.parent is not None:
                single_path.append(elem.data)
                elem = elem.parent
            if elem.parent is None:
                single_path.append(elem.data)
            # т.к. путь в обратном виде, разворачиваем
            single_path = single_path[::-1]
            for_debug = 0
            min_paths.append(single_path)
    min_paths.sort(key=lambda elem: get_date_from_row(elem[-1]))
    if int(one_or_all) == 1:
        if len(min_paths) > 1:
            return min_paths[0]
        else:
            return min_paths
    if int(one_or_all) == 2:
        return min_paths

def main():
    # сменить print на input
    date_initial = print("Введите дату в виде дд.мм.гггг\n")
    # date_initial = input("Введите дату в виде дд.мм.гггг\n")
    # date_initial = date_initial.split(".")
    # date_initial = dt.datetime(int(date_initial[2]), int(date_initial[1]), int(date_initial[0]))

    # origin = input("Введите IATA код аэропорта отправления\n")
    # dest = input("Введите IATA код аэропорта назначения\n")
    # date_initial = dt.datetime(2007, 10, 15)
    date_initial = dt.datetime(2000, 10, 15)
    date_final = get_date_final(date_initial)
    print(date_initial)
    print(date_final)
    # SAN-SFO
    # BUR-OAK
    # сан-франциско до екатеринбурга
    # DME домодедово PVD
    # SFO - SVX
    origin = "SFO"
    dest = "PVD"
    file_name = "C:/Users/user/Desktop/napoleon/data/" + str(date_initial.year) + ".csv"
    time_start = time.time()
    data = read_file(file_name, date_initial, date_final)
    # write_csv(data)
    print("считано рейсов " + str(len(data)))
    result = find_path(data, date_initial, origin, dest)
    result.sort(key=lambda elem: len(elem))
    # т.к. мы храним найденные пути не в виде списка, а в виде дерева, нужно привести к нормальному виду
    processed_result = list()
    # --------------------------------
    # if len(result) > 1:
    #     current = result[0]
    # else:
    #     current = result
    #
    # while len(current) > 1:
    #     processed_result.append(list(current.data))
    #     current = current.parent
    # processed_result.append(list(current.data))
    # processed_result = processed_result[::-1]
    # print("Найденные пути:")
    # print(processed_result)
    # print("найденные пути закончились")
    # --------------------------------
    time_finish = time.time()
    print("Время: " + str(time_finish - time_start))

    processed_result = get_optimal_path(result, 2)

    print(type(processed_result))
    write_csv(processed_result)

# выполняем основную программу


main()
# print(is_destination("AAA", list([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,"AAA"])))

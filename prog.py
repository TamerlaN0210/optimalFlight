import csv
import datetime as dt
import pandas as pd
import time

class revTree(object):
	"""Класс для хранения цепочки перелетов и удобного их считывания
	Корневой элемент должен иметь данные типа None"""
	def __init__(self, parent, data):
		self.parent = parent
		self.data = data

	def __len__(self):
		"""Возвращает количество узлов в ветви"""
		lenght = 0
		if self.parent == None:
			lenght = 1
		else:
			lenght = 1
			copy = self
			while copy.parent != None:
				copy = copy.parent
				lenght+=1
		return lenght

def isDestination(destination, flight):
	"""destination - IATA-код конечного аэропорта
	flight - полная информация о рейсе 
	Функция регистрозависимая"""
	# flight[17] - IATA-код аэропорта назначения текущего рейса
	if str(destination) == str(flight[17]):
		return True
	else:
		return False

def oneIter(data, previousFlight, alreadyBeen, pointDest):
	"""previousFlight - тип: revTree. Хранит информация о вершине, т.е. как мы прилетели в данный аэропорт"""
	
	paths = list() # маршруты, которые привели к точке назначения
	possibleFlights = list() #возможные рейсы из данного аэропорта
	previousFlightList = previousFlight.data
	currentPoint = previousFlightList[17] # куда мы прилетели
	arrivalDateTime = dt.datetime(int(previousFlightList[0]), int(previousFlightList[1]), int(previousFlightList[2]), int(previousFlightList[6][:-2]), int(previousFlightList[6][-2:]))
	temp = [] # хранит полеты только из данного аэропорта
	for row in data:
				#ищем маршруты из текущего аэропорта на заданное число, так, чтобы не попасть в аэропорты в коротые мы прибыли на других шагах
				#странное и непонятное время, пока будем просто удалять "битые" записи
				if(str(row[0]) == "" or str(row[1]) == "" or str(row[2]) == "" or str(row[6][:-2]) == "" or str(row[6][-2:]) == ""):
					print(row)
					continue
				try:
					rowDateTime = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(row[6][:-2]), int(row[6][-2:]))
				except ValueError as e:
					if int(row[6][:-2]) == 24:
						rowDateTime = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(0), int(row[6][-2:]))
				if str(row[16]) == str(currentPoint) and arrivalDateTime < rowDateTime and row[17] not in alreadyBeen:
					temp.append(row)
					# data.remove(row)
	if len(temp) == 0: # если исходящих рейсов нет, помечаем это путь как завершенный
		possibleFlights.append(revTree(previousFlight, "end"))
	else:
		while len(temp) > 0:
					currentFlight = temp[0]
					# добавляем аэропорты, из которых мы уже вылетали, чтобы не проходить их заново
					del temp[0]
					if len(temp) == 0: #если в списке полетов мы остался один рейс, которого нет у нас, то добавляем его у возможные пути
						possibleFlights.append(currentFlight)
						# проверяем, не прилетели ли мы уже в нужный аэропорт 
						if isDestination(pointDest, currentFlight):
							paths.append(revTree(None, currentFlight))
						break

					currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
					print(len(temp))
					
					for row in temp: 
						# 6-й элемент - время прибытия рейса
						# 21 и 23 - метки отмены рейса
						#if elem[17] == currentFlight[17] and compareTime(elem[6], currentFlight[6]) == -1:
						elemArrivalDateTime = dt.datetime(int(row[0]), int(row[1]), int(row[2]), int(row[6][:-2]), int(row[6][-2:]))
						if row[17] == currentFlight[17] and currentArrivalDateTime > elemArrivalDateTime:
							currentFlight = row
							currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
					# проверяем, не прилетели ли мы уже в нужный аэропорт 
					if isDestination(pointDest, currentFlight):
						paths.append(revTree(None, currentFlight))
					possibleFlights.append(revTree(None, currentFlight)) # заполнили список маршрутами из стартового аэропорта
	return paths, possibleFlights

def findPath(dataInput, date, pointOrig, pointDest):
	# data - список всех полетов за год в виде datetime
	# date - дата полета в виде datetime
	# pointOrig - IATA код аэропорта прибытия
	# pointDest - IATA код аэропорта назначения
	# Когда мы запускаем эту функцию, мы знаем из какого аэропорта, куда, и какого числа летим
	# Находим минимальный по кол-ву пересадок маршрут. и возвращаем его в виде списка с информацией о полете(ах)
	data = dataInput
	paths = list()# Найденные пути до пункта назначения
	alreadyBeen = set(pointOrig)# IATA-коды аэропортов, из которых мы уже вылетали на предыдущих шагах
	possibleFlights = list()# возможные маршруты из конкретной точки
	isDone = False
	#1. Убираем из поиска все полеты, которые были до введенной даты, они нас не интересуют
	# перенесли выборку в чтение файла
	print("Передано маршрутов в функцию " + str(len(data)))
	# for row in data:
	# 	if int(row[1]) >= int(date[1]):
	# 		if int(row[2]) >= int(date[2]):
	# 			possibleFlights.append(row)
	# data = possibleFlights
	# print("Данные которые нам нужны, т.е. после введенной даты: " + str(len(data)))

	currentFlight = [] #информация о конкретном полете
	temp = []  #временная
	startPosition = pointOrig
	while not isDone:
		firstMove = False #флаг для первого действия
		if firstMove == False:
			for row in data:
				#ищем маршруты из пункта отправки на заданное число, так, чтобы не попасть в аэропорты в коротые мы прибыли на других шагах
				if str(row[16]) == str(pointOrig) and int(date.month) == int(row[1]) and int(date.day) == int(row[2]):
					temp.append(row)
					data.remove(row)
			print("Вылетело из первого аэропора сегодня: " + str(len(temp)))

			# ищем возможные рейсы из начального аэропорта
			while len(temp) > 0:
				currentFlight = temp[0]
				# добавляем аэропорты, из которых мы уже вылетали, чтобы не проходить их заново
				# currentFlight[16] - IATA-код аэропорта отправления рейса
				alreadyBeen.add(currentFlight[16])
				del temp[0]
				if len(temp) == 0: #если в списке полетов мы остался один рейс, которого нет у нас, то добавляем его у возможные пути
					possibleFlights.append(currentFlight)
					# проверяем, не прилетели ли мы уже в нужный аэропорт 
					if isDestination(pointDest, currentFlight):
						paths.append(revTree(None, currentFlight))
					break

				currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
				# print(len(temp))
				
				# ниже логический цикл "for" оформлен как "while", для правильной итерации
				i = 0
				while i < len(temp): 
					# 6-й элемент - время прибытия рейса
					# 21 и 23 - метки отмены рейса
					#if elem[17] == currentFlight[17] and compareTime(elem[6], currentFlight[6]) == -1:
					elemArrivalDateTime = dt.datetime(int(temp[i][0]), int(temp[i][1]), int(temp[i][2]), int(temp[i][6][:-2]), int(temp[i][6][-2:]))
					if temp[i][17] == currentFlight[17] and currentArrivalDateTime > elemArrivalDateTime:
						currentFlight = list(temp[i])
						currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
						del temp[i]
					elif temp[i][17] == currentFlight[17] and currentArrivalDateTime <= elemArrivalDateTime:
						del temp[i]
					else:
						i+=1
				# проверяем, не прилетели ли мы уже в нужный аэропорт 
				if isDestination(pointDest, currentFlight):
					paths.append(revTree(None, currentFlight))
				possibleFlights.append(revTree(None, currentFlight)) # заполнили список маршрутами из стартового аэропорта
			firstMove = True
		while len(data) > 0:
			elemPaths = list() # найденные пути до точки назначения от данной вершины
			elemPossiblePaths = list() # все найденные пути из данного аэропорта 
			storedPaths = list() # все найденные пути до точки назначения от данной вершины на текущей глубине
			storedPossiblePaths = list() # все найденные пути из аэропортов на текущей глубине
			stroredAlreadyBeen = list() # аэропорты, из которых мы прилетели на текущей глубине
			for elem in possibleFlights:
				if elem.data != "end":
					elemPaths, elemPossiblePaths = oneIter(data, elem, alreadyBeen, pointDest)
					storedPaths.extend(elemPaths)
					storedPossiblePaths.extend(elemPossiblePaths)
				else:
					continue
			# сначала добавляем в пройденные аэропорты те, которые достигли на предыдущем шаге, чтобы меньше обходить
			for elem in possibleFlights:
				if elem.data != "end":
					if str(elem.data[17]) not in alreadyBeen:
						alreadyBeen.add(str(elem.data[17]))
				else:
					continue
			possibleFlights = storedPossiblePaths
			paths.extend(storedPaths)
			
			i = 0
			while i < len(data):
				if str(data[i][17]) in alreadyBeen:
					del data[i]
				else:
					i+=1

			# while len(data) > 0:
			# 	for row in possibleFlights:
			print(len(data))
		isDone = True
	#TODO вернуть найденные пути до точки назначения, а не просто все найденные пути, сейчас это заглушка
	# return possibleFlights
	return paths

def readFile(fileName, dateInitial, dateFinal):
	data = list()
	#data = pd.read_csv(fileName)
	# df = pd.concat(data, ignore_index=True)
	with open(fileName, "r", newline="") as file:
		reader = csv.reader(file)
		reader.__next__() #пропустили строку с названиями столбцов
		for row in reader:
			copy = row
			# если время прилета битое, пропускаем
			if(str(row[0]) == "" or str(row[1]) == "" or str(row[2]) == "" or str(row[6][:-2]) == "" or str(row[6][-2:]) == ""):
					continue
			#если месяц тот же и дата больше или равна, тогда добавляем
			# 21 и 23 - метки отмены рейса
			# для правильной обработки времени, меняем 24.00 текущей даты, на 00.00 следующего дня
			if int(copy[6][:-2]) == 24 and int(copy[6][-2:]) == 00:
				copy[6] = "0000"
				delta = dt.timedelta(1)
				copyDate = dt.datetime(int(copy[0]), int(copy[1]), int(copy[2])) + delta
				copy[0], copy[1], copy[2] = copyDate.year, copyDate.month, copyDate.day
			else:
				copyDate = dt.datetime(int(copy[0]), int(copy[1]), int(copy[2]))
			if dateInitial <= copyDate and dateFinal > copyDate and (int(copy[21]) != 1 and int(copy[23]) != 1):
				data.append(copy)
	return data
def compareTime(time1, time2):
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
def getDateFinal(dateInitial):
	"""dateInitial имеет тип datetime
	Возвращает дату большую на 2 дня в том же формате
	"""
	timedelta = dt.timedelta(2) # временной отрезок - 2 дня
	dateFinal = dateInitial + timedelta
	return dateFinal
def writeCsv(data):
	with open("output.csv", "w", newline="") as file:
		writer = csv.writer(file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		writer.writerows(data)
	pass

#main/////////////////////////////////////////////////////////////////////////////////////////
def main():
	# сменить print на input
	dateInitial = print("Введите дату в виде дд.мм.гггг\n")
	#dateInitial = input("Введите дату в виде дд.мм.гггг\n")
	#dateInitial = dateInitial.split(".")
	#dateInitial = dt.datetime(int(dateInitial[2]), int(dateInitial[1]), int(dateInitial[0]))

	#origin = input("Введите IATA код аэропорта отправления\n")
	#dest = input("Введите IATA код аэропорта назначения\n")
	# dateInitial = dt.datetime(2007, 10, 15)
	dateInitial = dt.datetime(1987, 10, 15)
	dateFinal = getDateFinal(dateInitial)
	print(dateInitial)
	print(dateFinal)
	# SAN-SFO
	# BUR-OAK 
	origin = "BUR"
	dest = "OAK"
	fileName = "C:/Users/user/Desktop/napoleon/data/" + str(dateInitial.year) + ".csv"
	timeStart = time.time()
	data = readFile(fileName, dateInitial, dateFinal)
	# writeCsv(data)
	print("считано рейсов " + str(len(data)))
	input()
	result = findPath(data, dateInitial, origin, dest)
	result.sort(key = lambda elem: len(elem))
	# т.к. мы храним найденные пути не в виде списка, а в виде дерева, нужно привести к нормальному виду
	processedResult = list()
	# for i in result:
	# 	if i.parent == None:
	# 		processedResult.append(i.data)
	# 	else:
	# 		while i.parent != None:
	# 			print("Такого быть не должно.")
	current = result[0]
	while len(current) > 1:
		processedResult.append(current.data)
		current = current.parent
	processedResult.append(current.data)
	processedResult = processedResult.reverse()

	timeFinish = time.time()
	print("Время: " + str(timeFinish - timeStart))
	processedResult.sort(key = lambda i: i[17])
	writeCsv(processedResult)

# выполняем основную программу
main() 
# print(isDestination("AAA", list([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,"AAA"])))
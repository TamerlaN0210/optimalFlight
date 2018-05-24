import csv
import datetime as dt
import pandas as pd

def findPath(data, date, pointOrig, pointDest):
	#data - список всех полетов за год в виде datetime
	#date - дата полета в виде datetime
	#pointOrig - IATA код аэропорта прибытия
	#pointDest - IATA код аэропорта назначения
	#Когда мы запускаем эту функцию, мы знаем из какого аэропорта, куда, и какого числа летим
	#Находим минимальный по кол-ву пересадок маршрут. и возвращаем его в виде списка с информацией о полете(ах)
	paths = list()#Найденные пути до пункта назначения
	alreadyBeen = set(pointOrig)#аэропорты в коротых уже были
	possibleFlight = list()#возможные маршруты из конкретной точки
	isDone = False
	#1. Убираем из поиска все полеты, которые были до введенной даты, они нас не интересуют
	# перенесли выборку в чтение файла
	print("Передано маршрутов в функцию " + str(len(data)))
	# for row in data:
	# 	if int(row[1]) >= int(date[1]):
	# 		if int(row[2]) >= int(date[2]):
	# 			possibleFlight.append(row)
	# data = possibleFlight
	# print("Данные которые нам нужны, т.е. после введенной даты: " + str(len(data)))

	possibleFlight = list()
	currentFlight = [] #информация о конкретном полете
	temp = []  #временная
	startPosition = pointOrig
	currentPos = list()
	while not isDone:
		firstMove = False #флаг для первого действия
		if firstMove == False:
			for row in data:
				#ищем маршруты из пункта отправки на заданное число, так, чтобы не попасть в аэропорты в коротые мы прибыли на других шагах
				if str(row[16]) == str(pointOrig) and int(date.month) == int(row[1]) and int(date.day) == int(row[2]):
					temp.append(row)
					data.remove(row)
			print("Вылетело из первого аэропора сегодня: " + str(len(temp)))
			while len(temp) > 0:
				currentFlight = temp[0]
				del temp[0]
				if len(temp) == 0:
					possibleFlight.append(currentFlight)
					break

				currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
				print(len(temp))
				i = 0
				while i < len(temp):
					# 6-й элемент - время прибытия рейса
					# 21 и 23 - метки отмены рейса
					#if elem[17] == currentFlight[17] and compareTime(elem[6], currentFlight[6]) == -1:
					elemArrivalDateTime = dt.datetime(int(temp[i][0]), int(temp[i][1]), int(temp[i][2]), int(temp[i][6][:-2]), int(temp[i][6][-2:]))
					#if elem[17] == currentFlight[17] and compareTime(elem[6], currentFlight[6]) == -1:
					if temp[i][17] == currentFlight[17] and currentArrivalDateTime > elemArrivalDateTime:
						print(currentFlight[:18])
						print(temp[i][:18])
						print(currentArrivalDateTime)
						print(elemArrivalDateTime)
						input()
						currentFlight = list(temp[i])
						currentArrivalDateTime = dt.datetime(int(currentFlight[0]), int(currentFlight[1]), int(currentFlight[2]), int(currentFlight[6][:-2]), int(currentFlight[6][-2:]))
						del temp[i]
					elif temp[i][17] == currentFlight[17] and currentArrivalDateTime <= elemArrivalDateTime:
						del temp[i]
					else:
						i+=1
				possibleFlight.append(currentFlight)
				alreadyBeen.add(currentFlight[17])
			firstMove = True
		
		isDone = True
	#TODO вернуть нормальное значение, сейчас это заглушка
	return possibleFlight

def readFile(fileName, dateInitial, dateFinal):
	data = list()
	#data = pd.read_csv(fileName)
	# df = pd.concat(data, ignore_index=True)
	with open(fileName, "r", newline="") as file:
		reader = csv.reader(file)
		reader.__next__() #пропустили строку с названиями столбцов
		for row in reader:
			#если месяц тот же и дата больше или равна, тогда добавляем
			# 21 и 23 - метки отмены рейса
			rowDate = dt.datetime(int(row[0]), int(row[1]), int(row[2]))
			if dateInitial <= rowDate and dateFinal > rowDate and (int(row[21]) != 1 and int(row[23]) != 1):
				data.append(row)
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
# сменить print на input
dateInitial = print("Введите дату в виде дд.мм.гггг\n")
#dateInitial = input("Введите дату в виде дд.мм.гггг\n")
#dateInitial = dateInitial.split(".")
#dateInitial = dt.datetime(int(dateInitial[2]), int(dateInitial[1]), int(dateInitial[0]))

#origin = input("Введите IATA код аэропорта отправления\n")
#dest = input("Введите IATA код аэропорта назначения\n")
dateInitial = dt.datetime(1987, 10, 15)
dateFinal = getDateFinal(dateInitial)
print(dateInitial)
print(dateFinal)
# SAN-SFO
# BUR-OAK 
origin = "BUR"
dest = "OAK"
fileName = "C:/Users/user/Desktop/napoleon/data/" + str(dateInitial.year) + ".csv"
data = readFile(fileName, dateInitial, dateFinal)
# writeCsv(data)
print("считано рейсов " + str(len(data)))
result = findPath(data, dateInitial, origin, dest)
result.sort(key = lambda i: i[17])
writeCsv(result)
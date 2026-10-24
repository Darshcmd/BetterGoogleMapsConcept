from distributedDjikstra import simulator, google_maps, better_google_maps
from utils.Graph import Graph
import csv
from utils.Person import Person

print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")


graph = Graph('test_graphs/graph7.csv')
graph2 = Graph('test_graphs/graph7.csv')

people = []
people2 = []


with open('test_persons/people7.csv', 'r') as file:
		reader = csv.reader(file)
		for row in reader:
			people.append(Person(row[0], row[1]))
			people2.append(Person(row[0], row[1]))

print("GOOGLE PATHS:")
google = simulator(graph, google_maps(graph, people))
# print(f"System Age for Google Maps:", google[0])
print(f"Avg Time Taken/Person for Google Maps:", google[1])
print("")
print("DARSH PATHS:")
better_google = simulator(graph2, better_google_maps(graph2, people2))
# print(f"System Age for Better Google Maps:", better_google[0])
print(f"Avg Time Taken/Person for BetterGoogleMaps Maps:", better_google[1])

print('\n\n\n')
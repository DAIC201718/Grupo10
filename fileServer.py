'''
Created on 6 de jun. de 2016

@author: inigo
'''
from flask import Flask, request, Response, abort
import thread
import json
import os
import time
from heapq import nsmallest
import math
import datetime

import itertools
import cmath
import numpy as np

app = Flask(__name__)

active_users = dict()

ibeacon_location = {
        "FF:7C:FA:0D:B0:29":(0,0),
        "C2:C7:7A:6E:89:B3":(2,3),
        "C6:1F:A8:28:B8:4E":(3,3),
        "D2:09:A9:42:DC:97":(5,6)
        }

light_location = [
        [(1,3),18],
        [(2.5,3),13],
        [(4,3),19]
        ]

@app.route('/ibeacon_location', methods=['POST'])
def ibeacon_communication():
    if not request.json:
        abort(400)
    content = request.get_json()
    #Save in elastic
    username = content['username'].replace(" ","_")
    content.pop('username', None)
    content.pop('FF:7C:FA:0D:B0:29', None)
    content.pop('D2:09:A9:42:DC:97', None)
    #print(content)
    location=calculate_location(content)
    active_users[username] = (location,2)
    millis=int(round(time.time()*1000))
    content['location_x']=location[0]
    content['location_y']=location[1]
    content['@timestamp']=str(datetime.datetime.now())
    elastic_post = 'curl -XPOST 192.168.1.100:9200/'+username+"/logs/"+str(millis)+" -H 'Content-Type: application/json' -d '"+str(content).replace("u'","'").replace("'",'"')+"'"
    print(elastic_post)
    os.system(elastic_post)
    #print(elastic_post)
    #print(active_users[username])
    return json.dumps(request.json)

#curl -i -H "Content-Type: application/json" -X POST -d '{"userId":"1", "username": "fizz bizz"}' http://localhost:8080/ibeacon_location

def calculate_location(distance_json):
    #Get top 3 smallest values
    '''
    Pasos a seguir -> Interseccion de los 3 circulos, dos a dos a,b + a,c -> Sacar recta en ambos sitios
    (x-a**2) + (y-aa**2) = R**2
    (x-b)**2 + (y-bb**2) = r**2
    Sacar interseccion entre rectas
    '''
    smallest3 = nsmallest(3, list(map(float,distance_json.values())))
    distance = dict()
    for key,value in distance_json.items():
        if len(distance)!=3 and value in smallest3:
            distance[key] = float(value)
    key_combinations =  list(itertools.combinations(distance.keys(), 2))
    key_combination_intersection = [is_circle_intersection(ibeacon_location[x],distance_json[x],ibeacon_location[y],distance_json[y]) for x,y in key_combinations]
    if(sum(key_combination_intersection)==0):
        #Error while taking data
        return (-99999,-99999)
    elif(sum(key_combination_intersection)<3):
        #print(key_combinations)
        keys = key_combinations[key_combination_intersection.index(True)]
        line1 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        #print(line1)
        line2=get_line_between_two_points(ibeacon_location[keys[0]],ibeacon_location[keys[1]])
        #print(line2)
        return get_intersection_between_lines(line1,line2)
    else:
        keys = key_combinations[0]
        line1 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        keys = key_combinations[1]
        line2 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        return get_line_between_two_points(line1,line2)

def solve_quadratic_equation(a,b,c):
    d = b**2-4*a*c # discriminant
    if d < 0:
        #There is no real number that satisfies the equation
        return -99999
    elif d == 0:
        x = (-b+math.sqrt(b**2-4*a*c))/2*a
        return x
    else:
        x1 = (-b+math.sqrt((b**2)-(4*(a*c))))/(2*a)
        x2 = (-b-math.sqrt((b**2)-(4*(a*c))))/(2*a)
        return [x1,x2]

def get_line_between_circles(circle1,radius1,circle2,radius2):
    line_between_points = get_line_between_two_points(circle1,circle2)
    distance_between_the_circles = get_distance_between_points(circle1, circle2)
    proportion_circle1 = radius1/distance_between_the_circles
    extra_distance_radius1 = [x*proportion_circle1 for x in get_distance_by_dimension_between_points(circle1,circle2)]
    points_circle1 = [\
            [x-y for x,y in zip(circle1,extra_distance_radius1)], \
            [x+y for x,y in zip(circle1,extra_distance_radius1)]\
            ]
    proportion_circle2 = radius1/distance_between_the_circles
    extra_distance_radius2 = [x*proportion_circle2 for x in get_distance_by_dimension_between_points(circle2,circle1)]
    points_circle2 = [\
            [x-y for x,y in zip(circle1,extra_distance_radius2)], \
            [x+y for x,y in zip(circle1,extra_distance_radius2)]\
            ]
    combinations_between_points = list(itertools.product(points_circle1,points_circle2))
    distances_combinations = [get_distance_between_points(x,y) for x,y in combinations_between_points]
    index_of_min_distance = distances_combinations.index(min(distances_combinations))
    #print(distances_combinations[index_of_min_distance])
    mean_point = [float((x+y)/2) for x,y in combinations_between_points[index_of_min_distance]]
    if line_between_points[0]==0:
        new_slope=-999999
    else:
        new_slope = -1/line_between_points[0]
    new_b = mean_point[1] - new_slope*mean_point[0]
    return [new_slope, new_b]




    '''
    #A**2,B**2,2AB
    line_between_points_squared = [x**2 for x in line_between_points]
    line_between_points.append(2*line_between_points[0]*line_between_points[1])
    radius = radius1
    x_squared = 1+line_between_points_squared[0]
    values = radius - line_between_points_squared[1] - line_between_points_squared[2]
    results_x = solve_quadratic_equation(1+line_between_points_squared[0],line_between_points_squared[2],line_between_points_squared[1]-radius**2)
    calculate_y = lambda x:line_between_points[0]*x+line_between_points[1]
    results_y = []
    '''

def get_distance_by_dimension_between_points(point1,point2):
    return [x-y for x,y in zip(point1,point2)]

def get_distance_between_points(point1,point2):
    return sum([(x-y)**2 for x,y in zip(point1,point2)])**.5

#OK
def get_line_between_two_points(point1, point2):
    x1,x2=point1[0],point2[0]
    y1,y2=point1[1],point2[1]
    slope = ((y1-y2)/(x1-x2))
    #b = (x1*y1 - x2*y1)/(x1-x2)
    b = y1-(x1*slope)
    #print(b==(y2-x2))
    return [slope,b]

#OK
def get_intersection_between_lines(line1,line2):
    if(line1[0] == line2[0]):
        print("Lines are parallel")
        x=-1
        y=-1
    else:
        x = float(line2[1]-line1[1])/(line1[0]-line2[0])
        y = line1[0]*x + line1[1]
    return (x,y)

#OK
def is_circle_intersection(circle1,radius1,circle2,radius2):
    ordered_radius = sorted([radius1,radius2])
    #Get hypotenuse
    distances = (abs(circle1[0]-circle2[0]),abs(circle1[1]-circle2[1]))
    inter_point_max_distance = math.sqrt(distances[0]**2+distances[1]**2)
    #Enough distance
    enough_distance = inter_point_max_distance < sum(ordered_radius)
    #Too much distance
    not_too_much_distance = inter_point_max_distance+ordered_radius[0] > ordered_radius[1]
    return enough_distance and not_too_much_distance

def light_up():
    while 1:
        time.sleep(1)
        #print("EXECUTION STARTING")
        for key, values in active_users.iteritems():
            if values[1]-1!=-1:
                active_users[key] = [values[0],values[1]-1]
                #print("VALORES A REDUCIR VALUES[DIST, NUMERO VUELTAS -1]",values)
            else:
                content.pop(key, None)
        if len(active_users) >0 :
            for location,pin in light_location:
                min_position = min([get_distance_between_points(value[0],location) for index,value in active_users.iteritems()])
                #print("DISTANCE MINIMUM TO ",location,"IS",min_position)
                if (min_position > 8):
                    luminosidad=100
                elif min_position<1: 
                    luminosidad=1000
                else:
                    luminosidad=300
                print("DISTANCE MINIMUM TO ",location,"IS",min_position,"CON LUMINOSIDAD",luminosidad)
                #print("VALOR LUMINOSIDAD", luminosidad)
                luminosidad_="gpio -g mode "+str(pin)+" pwm ; gpio -g pwm "+str(pin)+" "+str(luminosidad)
                #print("COMANDO A EJECUTAR",luminosidad_)
                os.system(luminosidad_)
                #print()


if __name__ == "__main__":
    thread.start_new_thread(light_up,())
    app.run(host='0.0.0.0', port=8080)

'''
Created on 6 de jun. de 2016

@author: inigo
'''
from flask import Flask, request, Response, abort
import json
import os
import time
from heapq import nsmallest
import math
import itertools

app = Flask(__name__)

active_users = dict()

ibeacon_location = {
        "FF:7C:FA:0D:B0:29":(0,0),
        "C2:C7:7A:6E:89:B3":(1,2),
        "C6:1F:A8:28:B8:4E":(3,4),
        "D2:09:A9:42:DC:97":(5,6)
        }

@app.route('/ibeacon_location', methods=['POST'])
def ibeacon_communication():
    if not request.json:
        abort(400)
    content = request.get_json()
    #Save in elastic
    content = content['username'].replace(" ","_")
    content.pop('username', None)
    print(content)
    millis = int(round(time.time() * 1000))
    elastic_post = 'curl -XPOST 127.0.0.1:9200/supermarket/'+content+"/"+str(millis)+" -d '"+str(content).replace("u'","'").replace("'",'"')+"'"
    os.system(elastic_post)
    active_users[content['username']] = (calculate_location(content),millis,False)
    return json.dumps(request.json)

#curl -i -H "Content-Type: application/json" -X POST -d '{"userId":"1", "username": "fizz bizz"}' http://localhost:8080/ibeacon_location

def calculate_location(distance_json):
    #Get top 3 smallest values    
    '''
    Pasos a seguir -> Interseccion de los 3 circulos, dos a dos a,b + a,c -> Sacar recta en ambos sitios
    (x-a**2) + (y-aa**2) = R**2
    (x-b)**2 + (y-bb**2) = r**2
    Sacar intersección entre rectas
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
        return (-1,-1)
    elif(sum(key_combination_intersection)<3):
        keys = key_combinations[key_combination_intersection.index(True)]
        line1 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        line2=get_line_between_two_points(ibeacon_location[keys[0]],ibeacon_location[keys[1]])
        return get_line_between_two_points(line1,line2)
    else:
        keys = key_combinations[0]
        line1 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        keys = key_combinations[1]
        line2 = get_line_between_circles(ibeacon_location[keys[0]],distance_json[keys[0]],ibeacon_location[keys[1]], distance_json[keys[1]])
        return get_line_between_two_points(line1,line2)



def get_line_between_circles(circle1,radius1,circle2,radius2):
    return [2*circle1[0]-2*circle2[0],2*circle1[1]-2*circle2[1],(circle1[0]**2+circle1[1]**2-radius1**2)-(circle2[0]**2+circle2[1]**2-radius2**2)]

def get_line_between_two_points(point1, point2):
    x1,x2=point1[0],point2[0]
    y1,y2=point1[1],point2[1]
    slope = ((y1-y2)/(x1-x2))
    b = (x1*y1 - x2*y1)/(x1-x2)
    return [slope,b]

def get_intersection_between_lines(line1,line2):
    if(line1[0] == line2[0]):
        print("Lines are parallel")
        x=-1
        y=-1
    else:
        x = (line2[1]-line1[1])/(line1[0]-line2[0])
        y = line1[0]*x + line1[1]
    return (x,y)
    
def is_circle_intersection(circle1,radius1,circle2,radius2):
    ordered_radius = sorted([radius1,radius2])
    inter_point_max_distance = 0 
    if (circle1[0] == circle2[0]):
        inter_point_max_distance = abs(circle2[0] - circle1[0])
    elif (circle2[0] == circle1[0]):
        inter_point_max_distance = abs(circle2[1] - circle1[1])
    else:
        #Get hypotenuse
        distances = (circle1[0]-circle2[0],circle1[1]-circle2[1])
        inter_point_max_distance = math.sqrt(distances[0]**2+distances[1]**2)  
    return inter_point_max_distance+ordered_radius[0] > ordered_radius[1]

def light_management():
    

if __name__ == "__main__":
    #threading.thread(target=)
    app.run(host='0.0.0.0', port=8080)
    

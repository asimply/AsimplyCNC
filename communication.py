#!/usr/bin/env python3
# encoding: utf-8

import serial
import time
import threading

from gi.repository import GLib, Gtk, GObject

#import mod.gui
import __main__

# Some usefull and common functions
def dist_2_points_2d(coord_a, coord_b):
    from math import sqrt
    distance_2d = ((coord_a [0]-coord_b[0])**2 + (coord_a [1]-coord_b[1])**2)**(1/2)
    return round(distance_2d, 2)

def dist_2_points_3d(coord_a, coord_b):
    from math import sqrt
    distance_3d = ((coord_a [0]-coord_b[0])**2 + (coord_a [1]-coord_b[1])**2 + (coord_a [2]-coord_b[2])**2)**(1/2)
    return round(distance_3d, 2)

def module_coordinate_3d(coord):
    from math import sqrt
    dist = sqrt((sqrt(coord[0]**2 + coord[1]**2))**2 + coord[2]**2)
    return dist
    
    
# Object that gets the increments, set the steps and harmonizes the speeds by a max speed given.
# Returns and order by the arduino programmation requeriments
class Order (object):
    
    def __init__(self, incrX, incrY, incrZ):
        self.posicion = __main__.posicion
        self.parameters = __main__.parameters
        
        self.incrX = incrX
        self.incrY = incrY
        self.incrZ = incrZ
        self.absincrX = abs(incrX)    # Incrementos en valor absoluto
        self.absincrY = abs(incrY)
        self.absincrZ = abs(incrZ)
        self.steps_rev = __main__.parameters.steps_rev  # Pasos para avanzar una unidad de medida
        self.vel_max = __main__.parameters.vel_max          # Velocidad máxima a la que podrá ir el eje que recorra mayor distancia
        self.get_steps()              # Obtiene los pasos para cada incremento
        self.get_speed()              # Obtiene las velocidades para cada eje según los incrementos
        
    def __str__(self):
        # Termina con un salto de linea para que arduino entienda que se acaba la orden
        return ("M1X" + str(self.stepsX) + "Y" + str(self.stepsY) + "Z" + str(self.stepsZ) + "U" + str(self.velU) + "V" + str(self.velV) + "W" + str(self.velW) + "\n")
    
    # Convierte los incrementos a pasos
    def get_steps(self):
        self.stepsX = int(self.absincrX * self.steps_rev) # Esto es el núm de pasos para incrementar una unidad
        self.stepsY = int(self.absincrY * self.steps_rev)
        self.stepsZ = int(self.absincrZ * self.steps_rev)
        return self.stepsX, self.stepsY, self.stepsZ
        
    # Calcula la velocidad en cada eje asignando al más rápido la Vmax
    def get_speed (self):
        #Comprueba donde se da el mayor incremento, ya que será la máxima velocidad
        #Y a partir de ahí armoniza las demás
        if (self.absincrX >= self.absincrY and self.absincrX >= self.absincrZ and self.incrX !=0 ):
            self.velU = int((self.vel_max) * (self.incrX / self.absincrX))
            self.velV = int(((self.incrY * abs(self.velU)) / self.absincrX))
            self.velW = int(((self.incrZ * abs(self.velU)) / self.absincrX))
        elif (self.absincrY >= self.absincrX and self.absincrY >= self.absincrZ and self.incrY !=0 ):
            self.velV = int((self.vel_max) * (self.incrY / self.absincrY))
            self.velU = int(((self.incrX * abs(self.velV)) / self.absincrY))
            self.velW = int(((self.incrZ * abs(self.velV)) / self.absincrY))
        elif (self.absincrZ >= self.absincrX and self.absincrZ >= self.absincrY and self.incrZ !=0 ):
            self.velW = int((self.vel_max) * (self.incrZ / self.absincrZ))
            self.velU = int(((self.incrX * abs(self.velW)) / self.absincrZ))
            self.velV = int(((self.incrY * abs(self.velW)) / self.absincrZ))
        else:
            self.velU = 0
            self.velV = 0
            self.velW = 0
        return self.velU, self.velV, self.velW
        
    # Convierte los incrementos a pasos
    def send_testing_max_dist(self):
        if self.parameters.max_dist > 0: # Check if is necessary split the order or not (max_dist == 0):
            #if max(abs(float(self.incrX)), abs(float(self.incrY)), abs(float(self.incrZ))) >= self.parameters.max_dist:# Check if any incr > max_dist:
            max_incr = max(abs(float(self.incrX)), abs(float(self.incrY)), abs(float(self.incrZ)))
            if max_incr >= self.parameters.max_dist:# Check if any incr > max_dist:
                from math import ceil #import math
                #float(max(self.incrX, self.incrY, self.incrZ))
                module = ceil(max_incr/self.parameters.max_dist) # Ceil function rounds up the number. It's necessary to converting to float for getting a float division result and round well with ceil
                self.stepsX = self.stepsX / module
                self.stepsY = self.stepsY / module
                self.stepsZ = self.stepsZ / module
                for vez in range(module):
                    self.send()
            else:
                self.send()
        elif self.parameters.max_dist == 0:
            self.send()
        else:
            print ("Error Distancia máxima", "la distancia máxima debe ser un número mayor o igual a 0")
            __main__.app.win.on_error_clicked("Error Distancia máxima", "la distancia máxima debe ser un número mayor o igual a 0")
    
    # Convierte los incrementos a pasos
    def send(self):
        self.serial = __main__.arduino
        
        try:
            if self.serial.connected == True:
                self.serial.flushInput()
                
                ##mensajeVuelta = send_machine()
                
                __main__.app.win.putMessageLabel("mensaje", "Orden enviada a CNC")
                __main__.app.win.putMessageLabel("order_sent", self)
                __main__.app.win.putMessageLabel("order_time", self.time())
                
                #self.serial.write_machine(self)
                self.serial.write(bytes(str(self), encoding="utf-8"))   #Envía dicha variable a Arduino
                
                print ("Order sent: ", str(self))
                #self.serial.flushInput()         #### Cleans the serial port
                mensajeVuelta = self.serial.read_machine()    # Leer el mensaje de respuesta
                while mensajeVuelta  == "":
                    pass
                
                #GObject.idle_add(self.update_aftersent, mensajeVuelta)
                self.update_aftersent(mensajeVuelta)
            else:
                print ("Sin conexion", "El puerto esta cerrado")
                
                #active_thread._Thread__stop()
                #active_thread.join()
                #print (threading.enumerate())
                #Gtk.join_main_thread()
                GObject.idle_add(self.update_aftersent, "El puerto esta cerrado")
                #__main__.app.win.on_error_clicked("Sin conexion", "El puerto esta cerrado")
                return
        except serial.SerialException:
            print ("Sin conexion", "No hay conexion por USB")
            GObject.idle_add(self.update_aftersent, "No hay conexion por USB")
            #__main__.app.win.on_error_clicked("Sin conexion", "No hay conexion por USB")
            return
                
    def update_aftersent(self, mensajeVuelta):
        if mensajeVuelta == "OK":
            print ("mensajeVuelta: ",mensajeVuelta)
            __main__.app.win.putMessageLabel("mensaje", mensajeVuelta) # Put the message in the label
            self.posicion.show ()    # Shows the new position
            self.posicion.increase_order(self)                        # Updates the new position
        else:
            print ("Ha habido algún problema.", "Arduino dice: " + mensajeVuelta)
            __main__.app.win.on_info_clicked("Ha habido algún problema.", "Arduino dice: " + mensajeVuelta)
                    
    def time(self):
        max_length = max (self.stepsX, self.stepsY, self.stepsZ)
        seconds = max_length / self.vel_max
        return seconds
        
        
# Entity as line or polyline that belongs to the canvas drawing
class Drawing_entity (object):
    
    def __init__(self):
        self.coords = [] # This must be cabsolute coordinates
        self.selected = False
        self.highlighted = False
        self.name = "entidad"
        self.depth = 0
      
    def __str__(self):
        return (str(self.coords))
        
    def add_position(self, position):
        self.position = position
    
    # Total length of the entity
    def get_route(self):
        total_length = 0
        # List of coords in absolute_coords list but moved one item to right, the last will be the first, the first the second, ...
        coords_moved = []
        coords_moved.append(self.coords[-1])
        [coords_moved.append(x) for x in self.coords[0:-1]]
            
        for coord, pre_coord in zip(self.coords, coords_moved):
            total_length += dist_2_points_3d (coord, pre_coord)
            total_length = round(total_length,2)
            print (total_length)
        
        return total_length
    
    # Get the time that takes tracing the total route of the entity
    def get_time(self, mm_x_sec):
        entity_time = self.get_route() / mm_x_sec
        
        return entity_time
    
    # Nearest coordinate of the entity from a given point in coordinates
    def nearest_coord (self, coord_ref):
        coord_nearest = coord_ref
        # First distance as possible, to test with the others
        distance_min = ((self.coords[0][0]-coord_ref[0])**2 + (self.coords[0][1]-coord_ref[1])**2)**(1/2)
        for coord in self.coords[1:]:
            distance = ((coord [0]-coord_ref[0])**2 + (coord [1]-coord_ref[1])**2)**(1/2)
            if distance < distance_min:
                distance_min = distance
                coord_nearest = coord
        if coord_nearest == coord_ref: # If the first coord was the nearest, set it as nearest coord
            coord_nearest = self.coords[0]
        return coord_nearest
    
    def restart_from(self, coord):
        new_zero_coord = self.coords.index(coord)
        part_prev = self.coords[:new_zero_coord]
        part_post = self.coords[new_zero_coord:]
        self.coords = part_post + part_prev
        
    def select(self):
        if self.selected == False:
            self.selected = True
        else:
            self.selected = False

# Drawing to execute on the CNC
class Drawing (object):
    
    def __init__(self):
        #GTK self.canvas = canvas                    # Canvas donde se mostrarán las lineas y polilineas
        self.parameters = __main__.parameters
        self.lista_coordenadas = []
        self.absolute_coords = []
        self.entities_list = []

        
    # Load a draw from a file
    def load_from_file(self):
        # Obtains the path from the filedialog:
        dialog = __main__.app.win.filechooserdialogopen
        response = dialog.run()
        #dialog.hide()
        if response == 1:
            ruta = dialog.get_filename()
            dialog.hide()
        else:
            dialog.hide()
            return
        
        self.file_to_coords(ruta)
        self.get_maximum()
        self.coords_to_text_area()
        self.get_entities()
        self.get_total_time()
        self.get_total_length()
        __main__.app.win.on_configure_treeview()
        __main__.app.win.canvas.on_configure()
        
    # File to list of coordinates (lista-coordenadas[])
    def file_to_coords(self, ruta):
        # Open the file of the previous path selected:
        draw_file = open(ruta,'r') #encoding="utf-8"?       
        # Reads the first line of the file:
        linea = draw_file.readline()
        pre_coordinate = [0, 0, 0]
        while linea!="":
            if (linea.find(" X") > -1 or linea.find(" Y") > -1 or linea.find(" Z")> -1):
                coordenadas = []
                if (linea.find(" X") > -1):
                    xValue = self.get_incr_value(linea, "X", pre_coordinate[0])
                else:
                    xValue = 0
                if (linea.find(" Y") > -1):
                    yValue = self.get_incr_value(linea, "Y", pre_coordinate[1])
                else:
                    yValue = 0
                if (linea.find(" Z") > -1):
                    zValue = self.get_incr_value(linea, "Z", pre_coordinate[2])
                else:
                    zValue = 0
                coordenada = [float(xValue), float(yValue), float(zValue)]
                coordenada = [(round(value, 4)) for value in coordenada]
                
                self.lista_coordenadas.append(coordenada)
                
                if str(ruta).endswith(".asc"): # If the file read is an asc don't accumulate values, they are already increments!
                    pre_coordinate = [0, 0, 0] 
                else:
                    pre_coordinate = [pre_coordinate[0] + coordenada[0],pre_coordinate[1] + coordenada[1], pre_coordinate[2] + coordenada[2]]
                    
            linea=draw_file.readline()
        self.get_abs_coords_from_rel()
        draw_file.close()
        
    # Load a draw from a file
    def coords_to_text_area(self):
        for coord in self.lista_coordenadas:
            __main__.app.win.insertTextTextView("textbuffer1", " X"+str(coord[0]) + " Y"+str(coord[1]) + " Z"+str(coord[2])  + "\n")
    
    # Obtiene el valor "valor" de una linea de gcode
    def get_incr_value (self, linea,  valor, currentValue):
        indice= (linea.index(valor))+1        # Se suma +1 para no tomar la letra de la coordenada
        indiceEsp = linea.find(" ", indice)
        longitud = linea.__len__()
        if indiceEsp > 0:                     # Si existe un espacio después del conjunto coordenada+valor
            valorAbs = linea[indice:indiceEsp]
            valor = round((float(valorAbs)-currentValue),5)
        else:                                 # Si no existe un espacio
            valorAbs = linea[indice:longitud-1]# No tomar el salto de linea
            valor = round((float(valorAbs)-currentValue),5)
        return valor
        
    # Coords to entities
    def get_entities (self):
        pre_z = self.max_z                 # Variable containing a previous value not 0

        num = 0                            # Starts the enumeration of the entities
        for coord in self.absolute_coords:
            
            if coord[2] != 0 and pre_z != 0:          # This is a line linking two entities
                pre_z = coord[2]                      # Keep as previous z coordinate
            elif coord[2] == 0 and pre_z != 0:        # Here begins a new entity
                new_entity = Drawing_entity()         # Creates a new entity
                new_entity.depth = pre_z
                new_entity.name = "Entidad_" + str(num)
                new_entity.coords.append(coord)       # Adds the coordinates to the new entity
                pre_z = coord[2]                      # Keep as previous z coordinate
                num += 1
            elif coord[2] == 0 and pre_z == 0:        # The new coordinate belongs to the previous entity
                new_entity.coords.append(coord)       # Adds the coordinates to the entity
                pre_z = coord[2]                      # Keep as previous z coordinate
            else:                                     # coord[2] != 0 and pre_z == 0: The entity finishes and a new linking line starts
                self.entities_list.append(new_entity) # Adds the entity to the entities list
                pre_z = coord[2]                      # Keep as previous z coordinate
    
    # Updates the coordinates of each entity in relation with the order of the drawing
    def update_entities(self):
        origin = [0.0, 0.0, 0.0]
        for entity in self.entities_list:
            origin_e = entity.nearest_coord(origin)
            entity.restart_from(origin_e)
            origin = origin_e

    # Obtiene coordenadas de area de texto : return coordenadas
    def get_rel_coords(self):
        self.lista_coordenadas [:] = []
        start = self.absolute_coords[0]
        self.lista_coordenadas.append(start)

        for coord in self.absolute_coords[1:]:
            new_rel_coordX = round(coord[0] - start[0], 4)
            new_rel_coordY = round(coord[1] - start[1], 4)
            new_rel_coordZ = round(coord[2] - start[2], 4)
            self.lista_coordenadas.append([new_rel_coordX, new_rel_coordY, new_rel_coordZ])
            start = coord[0], coord[1], coord[2]
    
    # Obtiene coordenadas de area de texto : return coordenadas
    def get_abs_coords_from_rel(self):
        #self.absolute_coords [:] = []
        start = self.lista_coordenadas[0]
        self.absolute_coords.append(start)

        for coord in self.lista_coordenadas[1:]:
            new_abs_coordX = round(start[0] + coord[0], 4)
            new_abs_coordY = round(start[1] + coord[1], 4)
            new_abs_coordZ = round(start[2] + coord[2], 4)
            self.absolute_coords.append([new_abs_coordX, new_abs_coordY, new_abs_coordZ])
            start = new_abs_coordX, new_abs_coordY, new_abs_coordZ
            #print ("new_abs_coordX, new_abs_coordY, new_abs_coordZ", new_abs_coordX, new_abs_coordY, new_abs_coordZ)
    
    # Obtiene coordenadas de las entidades
    def get_abs_coords_from_entities(self):
        self.absolute_coords [:] = []
        origin = [0, 0, self.max_z]
        self.absolute_coords.append(origin)
        
        for entity in self.entities_list:
            origin_e = entity.coords[0]
            #origin_e = entity.nearest_coord(origin)
            self.absolute_coords.append([origin_e[0], origin_e[1], self.max_z])
            depth = self.max_z-float(entity.depth)
            #self.absolute_coords.append([origin_e[0], origin_e[1], depth])
            for coord in entity.coords:
                self.absolute_coords.append([coord[0], coord[1], depth])
            self.absolute_coords.append([entity.coords[-1][0], entity.coords[-1][1], self.max_z])
            #self.absolute_coords.append([origin_e[0], origin_e[1], self.max_z])
            origin = origin_e
            
            
    # Obtiene coordenadas de area de texto : return coordenadas
    def get_coords_from_text_area(self):
        self.delete_drawing()           # First delete all previous values
        start = __main__.app.win.textbuffer.get_start_iter()
        end = __main__.app.win.textbuffer.get_end_iter()
        coordenadas = []
        
        while True:
            try:
                Xpos = start.forward_search("X", 0, end) # returns the list of the two positions after and behind the search
                if Xpos == None:
                    print ("Text view ended")
                    break
                else:
                    # Creates the list for the current coordinate
                    coordenada = []
                    
                    # Get the X value
                    start = Xpos[1]
                    Xendpos = start.forward_search(" ", 0, end) 
                    contenidoX = __main__.app.win.textbuffer.get_text(Xpos[1], Xendpos[0], True)
                    coordenada.append(float(contenidoX))
                    start = Xendpos[1]
                    
                    # Get the Y value
                    Ypos = start.forward_search("Y", 0, end)
                    start = Ypos[1]
                    Yendpos = start.forward_search(" ", 0, end)
                    contenidoY = __main__.app.win.textbuffer.get_text(Ypos[1], Yendpos[0], True)
                    coordenada.append(float(contenidoY))
                    start = Yendpos[1]
                    
                    # Get the Z value
                    Zpos = start.forward_search("Z", 0, end)
                    start = Zpos[1]
                    Zendpos = start.forward_search("\n", 0, end)
                    contenidoZ = __main__.app.win.textbuffer.get_text(Zpos[1], Zendpos[0], True)
                    coordenada.append(float(contenidoZ))
                    start = Zendpos[1]
                    
                    # appends the completed current coordinate to the coordinates list
                    coordenadas.append(coordenada)
            except:
                print ("The text is not X0.0 y0.0 Z0.0 format")
                __main__.app.win.on_error_clicked( "G-code Error", "The text is not X0.0 Y0.0 Z0.0 format")
                break
        
        # Replaces the coordinates list by the new created one
        self.delete_drawing()
        self.lista_coordenadas [:] = coordenadas [:]
        self.get_abs_coords_from_rel()      # Also for the absolute coordinates
        
        #return coordenadas
        
    # Guarda las órdenes leidas en este programa
    def save_draw_to_file(self):
        # Obtains the path from the filedialog:
        dialog = __main__.app.win.filechooserdialogsave
        response = dialog.run()
        if response == 1:
            ruta = dialog.get_filename()
            dialog.hide()
        else:
            dialog.hide()
            return
        draw_to_save = open(ruta,'w')
        content = __main__.app.win.getTextTextView("text_area")
        draw_to_save.write(content)
        draw_to_save.close()
        return
        
    # Draw the drawing coords in the canvas
    def draw_in_canvas (self):
        # Get the scale for adjusting the drawing and the wortable to the canvas
        drawing_scale = __main__.app.win.canvas.get_scale(self.max_x, self.max_y)
        worktable_scale = __main__.app.win.canvas.get_scale(__main__.worktable.limit_x, __main__.worktable.limit_y)
        
        if drawing_scale <= worktable_scale:
            __main__.app.win.canvas.set_scale(drawing_scale)
        else:
            __main__.app.win.canvas.set_scale(worktable_scale)
        
        # Draws the drawing
        origin = [0, 0, 0]
        color_line = (0, 255, 0) # Makes the first line in green
        for entity in self.entities_list:
            origin_e = entity.nearest_coord(origin)
            __main__.app.win.canvas.draw_line(origin, origin_e, color_line = color_line)
            color_line = (255, 0, 0) # Rest of lines in red
            
            if entity.highlighted == True: # If the entity is selected, draw in blue
                __main__.app.win.canvas.draw_polyline(entity.coords, line_width = 4, color_line = (0, 0, 255))
            else: # Else draw in black
                __main__.app.win.canvas.draw_polyline(entity.coords, color_line = (0, 255, 255))
            origin = origin_e
        
    # Return and store the max displacement of x and y
    def get_maximum (self):
        self.max_x = sum([coord[0] for coord in self.lista_coordenadas])
        self.max_y = sum([coord[1] for coord in self.lista_coordenadas])
        self.max_z = sum([coord[2] for coord in self.lista_coordenadas])
        return [self.max_x, self.max_y, self.max_z]
        
    # Return and store the total time for taking the drawing done
    def get_total_time (self):
        self.max_length_axis = sum([max(map(abs, coord))for coord in self.lista_coordenadas])
        self.total_time = self.max_length_axis / (self.parameters.vel_max / self.parameters.steps_rev)
        __main__.app.win.putMessageLabel("total_time", "%.2f min" %(self.total_time/60))
        return ("%.2f seg" %(self.total_time)) # "%.2f" %number formatea el número a dos decimales
        
    # Return and store the total length for taking the drawing done
    def get_total_length (self):
        total_length = 0
        # List of coords in absolute_coords list but moved one item to right, the last will be the first, the first the second, ...
        absolute_coords_moved = []
        absolute_coords_moved.append(self.absolute_coords[-1])
        [absolute_coords_moved.append(x) for x in self.absolute_coords[0:-1]]
            
        for coord, pre_coord in zip(self.absolute_coords, absolute_coords_moved):
            total_length += dist_2_points_3d (coord, pre_coord)
            total_length = round(total_length,2)
        
        __main__.app.win.putMessageLabel("total_length", total_length) # "%.2f mm" %(self.max_length))
        return total_length # ("%.2f mm" %(self.max_length)) # "%.2f" %number formatea el número a dos decimales
        
    # Delete the text area
    def delete_drawing (self):
        self.lista_coordenadas [:] = []
        self.absolute_coords [:] = []
        self.entities_list [:] = []
        self.max_length = 0
        self.max_length_axis = 0
        self.max_x = 0
        self.max_y = 0
        self.total_time = 0
        
    # Delete the canvas
    def delete_canvas (self):
        self.canvas.delete("all")
        
    # update_from_text_area, canvas, lista_coordenadas, total time, total length
    def update_from_text_area (self):
        self.delete_canvas()
        self.get_coords_from_text_area()
        self.get_maximum()
        self.get_total_time()
        self.get_total_length()
    
    def update_drawing(self):
        self.update_entities()
        self.get_abs_coords_from_entities()
        self.get_rel_coords()
        __main__.app.win.clearTextView()
        self.coords_to_text_area()
        

class Position (object):
    
    def __init__(self):
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        
    def __str__(self):
        return ("X" + str(self.pos_x) + " Y" + str(self.pos_y) + " Z" + str(self.pos_z))
    
    # Return a list with the coordinates of the actual position
    def get_position(self):
        return [self.pos_x, self.pos_y, self.pos_z]
        
    # Resets position to 0
    def reset (self):
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        
    # Incrementa la posición según una secuencia de parámetros
    def increase (self, incr_x = 0.0, incr_y = 0.0, incr_z = 0.0):
        self.pos_x += incr_x
        self.pos_y += incr_y
        self.pos_z += incr_z
    
    # Incrementa la posición según una orden
    def increase_order (self, order):
        self.pos_x += order.incrX
        self.pos_y += order.incrY
        self.pos_z += order.incrZ
        
    # Defines when the position gets out of the worktable
    def in_limits (self, worktable):    # Quizás worktable debería ser una propiedad de posición en __init__
        self.wortable = worktable
        if (0 > self.pos_x + incr_x) or (self.pos_x + incr_x > worktable.limit_x):
            #messagebox.showerror("Excedida dimensión en X", "El incremento en X excede los límites")
            return "Exceso en X"
            # Pedir acción al usuario sobre si seguir o parar
        if self.pos_y + incr_y> worktable.limit_y:
            messagebox.showerror("Excedida dimensión en Y", "El incremento en Y excede los límites")
        if self.pos_z + incr_z> worktable.limit_z:
            messagebox.showerror("Excedida dimensión en Z", "El incremento en Z excede los límites")
    
    # Shows the position in the Tkinter variables passed as parameters
    def show (self):
        __main__.app.win.putMessageLabel("xvalue", "%.4f" % round(self.pos_x, 4))
        __main__.app.win.putMessageLabel("yvalue", "%.4f" % round(self.pos_y, 4))
        __main__.app.win.putMessageLabel("zvalue", "%.4f" % round(self.pos_z, 4))
        
   
class Worktable (object):
    def __init__(self, limit_x, limit_y, limit_z):
        self.limit_x = limit_x
        self.limit_y = limit_y
        self.limit_z = limit_z
    
    # Creo que esto es una propiedad de la posición, no de worktable y por tanto se define alli.
    def out_limits (self):
        pass
    
    """def draw_worktable(self):
        __main__.app.canvas.draw_rectangle((self.limit_x, self.limit_y))"""


# Creates a communication with the machine
class Machine (serial.Serial):
    
    def __init__(self, rutaArduino, baudeArduino):
        #gtk self.position = __main__.posicion
        self.parameters = __main__.parameters
        
        self.rutaArduino = rutaArduino
        self.baudeArduino = baudeArduino
        self.connected = False
        #serial.Serial.__init__(self, rutaArduino, baudeArduino)
    
    # Connect with machine ####
    def conectar (self):
        try:
            #global arduino
            serial.Serial.__init__(self, self.rutaArduino, self.baudeArduino)
            #self = serial.Serial(self.rutaArduino, self.baudeArduino) #, bytesize=8, stopbits=1, timeout=0.1, xonxoff=0, rtscts=0, interCharTimeout=None)
            #self.open()
            time.sleep(1)
            self.getPort()
            print ("Conectado", "Se ha abierto el puerto en " + self.name)
            __main__.app.win.on_info_clicked( "Conectado", "Se ha abierto el puerto en " + self.name)
            self.connected = True
            return self
        except serial.SerialException:
            print ("Error al conectar. Sin conexion", "No hay conexion por USB")
            __main__.app.win.on_error_clicked( "Sin conexion", "No hay conexion por USB")
    
    # Reconectar a Arduino ####
    def reconectar(self):
        try:
            if self.isOpen() == 0:
                self.open()
                time.sleep(2)
                #GTK self.getPort()
                print ("Conectado", "Se ha abierto el puerto en " + self.name)
                __main__.app.win.on_info_clicked("Conectado", "Se ha abierto el puerto en " + self.name)
                self.connected = True
            else:
                print ("Ya conectado", "Ya está conectado a " + self.name)
                __main__.app.win.on_error_clicked("Ya conectado", "Ya está conectado a " + self.name)
        except serial.SerialException:
            print ("Error al reconectar. Sin conexion", "No hay conexion por USB")
            __main__.app.win.on_error_clicked("Sin conexion", "No hay conexion por USB")
            
    # Desconectar Arduino ####    
    def desconectar(self):
        try:
            self.close()
            time.sleep(1) # waiting the closing...
            if self.isOpen() == 0:
                print ("Sin conexion", "El puerto esta cerrado")
                __main__.app.win.on_info_clicked("Sin conexion", "El puerto esta cerrado")
                self.getPort()
                self.connected = False
            else:
                print ("Conectado", "No se ha podido cerrar")
                __main__.app.win.on_error_clicked("Conectado", "No se ha podido cerrar")
                self.connected = True
                self.getPort()
        except serial.SerialException:
            print ("Error en el cierre", "No se ha podido cerrar")
            __main__.app.win.on_error_clicked("Error en el cierre", "No se ha podido cerrar")
            
    
    # Escribir mensaje en Arduino
    def write_machine (self, message):
        try:
            if self.isOpen() == 1:
                self.flushInput()
                self.write(bytes(str(message), encoding="utf-8"))   #Envía el mensaje a Arduino
                return message
            else:
                print ("Sin conexion, el puerto esta cerrado. No s epudo enviar ", message)
                __main__.app.win.on_error_clicked("Sin conexion", "El puerto esta cerrado")
        except serial.SerialException:
            print ("Sin conexion, no esta conectado")
            __main__.app.win.on_error_clicked("Sin conexion", "Error: No esta conectado")
            
    # Leer mensaje de Arduino
    def read_machine (self):
        try:
            if self.isOpen() == 1:
                message_machine = self.readline()
                message_machine = str(message_machine,"ascii")
                indice = message_machine.find("\r")
                message_machine = message_machine[:indice]
                #arduino.flush() ###############
                #arduino.flushInput() ###############
                #arduino.flushOutput() ###############
                return message_machine
            else:
                print ("Sin conexion, el puerto esta cerrado")
                __main__.app.win.on_error_clicked("Sin conexion", "El puerto esta cerrado")
        except serial.SerialException:
            print ("Sin conexion, no esta conectado")
            __main__.app.win.on_error_clicked("Sin conexion", "Error: No esta conectado")
    
    
    # Averigua el puerto de Arduino y lo pone en la variable mensajeArduino
    def getPort(self):
        if self.isOpen() == 1:
            __main__.app.win.putMessageStatusBar("Conectado a " + self.name)
            return self.name
            #__main__.app.win.statusbar.push( self.name)
            #self.message_id = self.statusbar.push(0, "Updated Status Bar")
            #GTK return ("hola", self.name)
            #GTK __main__.mensajeArduino.set_text(self.name)
            #GTK self.gui.mensajeArduino.set(self.name)
        else:
            #GTK return "sin conexion"
            print ("Sin conexion, no hay puerto")
            __main__.app.win.putMessageStatusBar("sin conexion")


# Cálculos y acciones de movimiento ##############################
class Move_instructions(object):
    
    def __init__(self):
        self.isSentToCNC = False
        self.posicion = __main__.posicion
        self.parameters = __main__.parameters
        #self.gui = __main__.gui
        self.drawing = __main__.drawing
        self.inicioCNC = 0 # If pauses, keeps the coord for continuing
        self.serial = __main__.arduino
    
    def check(self):
        self.move_check = threading.Thread(target=self._check)
        self.move_check.start()
        
    def new_zero(self):
        self.posicion.reset()                                      # Situación actual a 0
        self.posicion.show()
        __main__.app.win.putMessageLabel("spinvalX", 0)
        __main__.app.win.putMessageLabel("spinvalY", 0)
        __main__.app.win.putMessageLabel("spinvalZ", 0)
        
    def sendMove(self): #GTK , event):
        self.move_thread = threading.Thread(target=self._mover)
        self.move_thread.start()
    
    def sendToOrigin(self):
        tOrigin = threading.Thread(target=self._toOrigin)
        tOrigin.start()
    def playCNC(self): #GTK , event):
        if self.serial.connected == True:
            self.isSentToCNC = True
            tplayCNC = threading.Thread(target=self._playCNC)
            tplayCNC.daemon = True
            tplayCNC.start()
        else:
            print ("Sin conexion", "El puerto esta cerrado")
            __main__.app.win.on_error_clicked("Sin conexion", "La máquina debe estar conectada")
            return
    def pauseCNC(self): #GTK , event):
        self.isSentToCNC = False
    def stopCNC(self): #GTK , event):
        self.isSentToCNC = False
        self.inicioCNC = 0
        
    def _check(self):

        try:
            if self.serial.connected == True:
                
                #mensajeVuelta = send_machine()
                #orden = "M1X600Y0Z0U600V0W0"
                #orden = Order(1, 1, 1)
                orden = "CHECK\n"
                self.serial.write_machine(orden)
                print ("Order sent: ", orden)
                #self.serial.flushInput()         #### Cleans the serial port
                mensajeVuelta = self.serial.read_machine()    # Leer el mensaje de respuesta
                while mensajeVuelta  == "":
                    pass
                if mensajeVuelta == "OK":
                    print (" Estado de la conexión: ",mensajeVuelta)
                    __main__.app.win.putMessageLabel("mensaje", mensajeVuelta) # Put the message in the label
                    #__main__.app.win.on_info_clicked("Estado de la conexión", "Arduino dice: " + mensajeVuelta)
                else:
                    print ("Ha habido algún problema.", "Arduino dice: " + mensajeVuelta)
                    #__main__.app.win.on_info_clicked("Ha habido algún problema.", "Arduino dice: " + mensajeVuelta)
                self.serial.flushOutput()
            else:
                print ("Sin conexion", "El puerto esta cerrado")
                active_thread = threading.current_thread()#threading.enumerate())
                if active_thread.isAlive():
                    try:
                        active_thread._Thread__stop()
                    except:
                        print(str(active_thread.getName()) + ' could not be terminated')
        except serial.SerialException:
            print ("Sin conexion", "No hay conexion por USB")
            #__main__.app.win.on_error_clicked("Sin conexion", "No hay conexion por USB")
        
        
    def _mover(self):
        if (__main__.paramOpened >= 1):          #Se ha visitado la ventana de parametros
            # Creates an Order from the increments introduces in the boxes passing it the steps/ud and max speed
            orden0 = [spin for spin in (__main__.app.win.getLabelValue("spinvalX"), __main__.app.win.getLabelValue("spinvalY"), __main__.app.win.getLabelValue("spinvalZ"))]
            orden = [float(value) for value in orden0]
            print (orden)
            orden = Order (orden[0], orden[1], orden[2])
            
            __main__.app.win.putMessageLabel("mensaje","Orden enviada a CNC" )
            __main__.app.win.putMessageLabel("order_sent", orden)
            __main__.app.win.putMessageLabel("order_time", orden.time())
            
            orden.send_testing_max_dist()
            __main__.app.win.putMessageLabel("order_sent", "")        # Clean order_sent message
            __main__.app.win.putMessageLabel("order_time", "") # Clean order_time message

        else:
            __main__.app.win.on_error_clicked("Falta configuración", "Se deben configurar los parámetros.\n Ir a Editar/Parametros")
            #GTK messagebox.showerror("Falta configuración", "Se deben configurar los parámetros.\n Ir a Editar/Parametros")
            
    # Mueve hasta el origen
    def _toOrigin(self):
        # Situación actual a 0
        movimientoX = 0 - self.posicion.pos_x
        movimientoY = 0 - self.posicion.pos_y
        movimientoZ = 0 - self.posicion.pos_z
        print (movimientoX, movimientoY, movimientoZ)
        orden = Order (movimientoX, movimientoY, movimientoZ)
        orden.send_testing_max_dist()
        print ("self.posicion", self.posicion)
        
        print ("CNC en origen")
    
    
    def _playCNC(self):
        self.drawing.get_coords_from_text_area() # updates the lista_coordenadas from the text_area
        coordenadas = self.drawing.lista_coordenadas
        for coordenada in range(self.inicioCNC, len(coordenadas)):
            if not self.isSentToCNC:
                #__main__.app.win.on_error_clicked("Trabajo parado", "La CNC ha parado")
                self.inicioCNC = coordenada
                break

            orden = Order (coordenadas[coordenada][0], coordenadas[coordenada][1], coordenadas[coordenada][2])
            orden.send_testing_max_dist()
        
        print ("Trabajo parado.", "La CNC ha terminado o esta en pausa.")
        return
        

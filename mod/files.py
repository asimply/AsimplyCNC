#!/usr/bin/env python3
# encoding: utf-8

import os
from tkinter import messagebox

class File(object):
    def __init__(self, path):
        self.path = path
    
    def read_file(self):
        self.content = ""
        for line in open (self.path,'r'):
            self.content += line
        return self.content
        
    def write_file(self, content_to_write):
        file_to_update = open (self.path,'w')
        file_to_update.write(content_to_write)
        file_to_update.close()
        
    def file_to_dict (self):
        dict_from_file = {}
        for line in open (self.path,'r'):
            name, value = line.split("=")
            value = value.strip()
            if value.isdigit():
                value = int(value)
            dict_from_file [name] = value
            #print (paramDict)
        return dict_from_file
    
    # Writes the dict into a file
    def dict_to_file (self, dict_to_file):
        dict_content = ""
        self.write_file(dict_content)
        for key, value in dict_to_file.items():
            dict_content += (str(key) + "=" + str(value) + "\n")
        self.write_file(dict_content)
        

class SVGFile(File):
    def __init__(self, path):
        File.__init__(self, path)
        self.path = path
    
    def extract_objects(self):
        self.objects_list = []
        
        
class Parameters (object):
    
    def __init__(self):
        if __name__ == "__main__":
            self.parameters = File("../parameters/parameters.txt")
        else:
            self.parameters = File("./parameters/parameters.txt")
        self.update_from_file()
        
    def update_from_file(self):
        self.param_dict = self.parameters.file_to_dict()
        try:
            self.vel_max = self.param_dict["vel_max"]
            self.steps_rev = self.param_dict["steps_rev"]
            self.dimX_max = self.param_dict["dimX_max"]
            self.dimY_max = self.param_dict["dimY_max"]
            self.dimZ_max = self.param_dict["dimZ_max"]
            self.ruta_arduino = str(self.param_dict["ruta_arduino"])
            self.baude_arduino = str(self.param_dict["baude_arduino"])
            self.placa_arduino = str(self.param_dict["placa_arduino"])
            self.max_dist = float(self.param_dict["max_dist"])
        except  (KeyError, RuntimeError, TypeError, NameError):
            self.return_default()
            messagebox.showerror("Error archivo preferencias", "El archivo de parámetros ha sido recreado desde cero")
    
    # Updates the dict with the new values changed by user
    def update_dict (self):
        self.param_dict = self.parameters.file_to_dict()
        self.param_dict["vel_max"] = self.vel_max
        self.param_dict["steps_rev"] = self.steps_rev
        self.param_dict["dimX_max"] = self.dimX_max
        self.param_dict["dimY_max"] = self.dimY_max
        self.param_dict["dimZ_max"] = self.dimZ_max
        self.param_dict["ruta_arduino"] = self.ruta_arduino
        self.param_dict["baude_arduino"] = self.baude_arduino
        self.param_dict["placa_arduino"] = self.placa_arduino
        self.param_dict["max_dist"] = self.max_dist
        
    # Rewrites the parameters.txt file to the defaults values
    def return_default(self):
        self.parameters.write_file("vel_max=600\nsteps_rev=600\ndimX_max=600\ndimY_max=600\ndimZ_max=60\nruta_arduino=/dev/ttyACM0\nbaude_arduino=9600\nplaca_arduino=UNO\nmax_dist=54.0")
        self.update_from_file()
    
    # Saves the new configuration in a separte file called parameters_custom.txt
    def save_configuration(self):
        # Saves new configuration to file
        self.update_dict()
        self.parameters.dict_to_file(self.param_dict)

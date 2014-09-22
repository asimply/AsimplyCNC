'''
Created on 15/08/2014

@author: fer by asimply.com
'''

#!/usr/bin/env python3
# encoding: utf-8

import sys
import serial
import time
import os
import threading
import math

try:
    from gi.repository import Gtk, GLib, Gio, GObject, Gdk
    import cairo
except:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    messagebox.showerror("GTK+3 or cairo are not installed", "Try sudo apt-get install python3-gi, python3-gi-cairo, python3-gi-dgb or search the web")
    print("GTK+3 or cairo are not installed")
    sys.exit(1)

# Import local modules
import mod.communication as comm
import mod.files as files

class Canvas(Gtk.DrawingArea):
    # The canvas
    def __init__(self):
        Gtk.DrawingArea.__init__(self)

        # Create buffer
        self.double_buffer = None
        self.scale = 1
        
        self.connect("draw", self.on_draw)
        self.connect("configure-event", self.on_configure_event)

        self.show()

        
    def on_draw(self, widget, cr):
        #Throw double buffer into widget drawable

        if self.double_buffer is not None:
            cr.set_source_surface(self.double_buffer, 0.0, 0.0)
            cr.paint()
        else:
            print('Invalid double buffer')

        return False
    
    def on_configure_event(self, widget, event, data=None):
        self.on_configure()

    def on_configure(self):
        #Configure the double buffer based on size of the widget

        # Destroy previous buffer
        if self.double_buffer is not None:
            self.double_buffer.finish()
            self.double_buffer = None

        # Create a new buffer
        self.double_buffer = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.get_allocated_width(), self.get_allocated_height())
        
        ### Added ###
        db = self.double_buffer
        if db is not None:
            # Create cairo context with double buffer as is DESTINATION
            self.cairo_ctx = cairo.Context(db)
            
            # Scale to device coordenates
            #width = db.get_width()
            #height = db.get_height()
            #self.cairo_ctx.scale(db.get_width(), db.get_height())

        else:
            print('Invalid double buffer')
        ### Added ###
        
        
        # Draw the drawinf if exist
        if drawing.entities_list != []:
            drawing.draw_in_canvas()
        # Draw the the worktable    
        self.draw_rectangle((worktable.limit_x, worktable.limit_y))

        return False
    
    
    # Deletes the buffer and the context
    def empty_canvas(self):
        #Configure the double buffer based on size of the widget
        # Destroy previous buffer
        if self.double_buffer is not None:
            self.double_buffer.finish()
            self.double_buffer = None
            self.cairo_ctx = None
            #self.on_configure()
        return
        
    # Draws a polyline in the canvas from a coordinate list
    def draw_polyline(self, coordinates_list, line_width = 1, color_line = (0,0,0)):
        #self.cairo_ctx.move_to(0,0)
        
        for coordinate in coordinates_list:
            self.cairo_ctx.line_to(self.scale * coordinate[0], self.scale * coordinate[1])
        
        self.cairo_ctx.set_source_rgb(color_line[0], color_line[1], color_line[2])
        self.cairo_ctx.set_line_width(line_width)
        
        self.cairo_ctx.stroke()
        
        self.double_buffer.flush()
    
    # Draws a line in the canvas from two points
    def draw_line(self, point_a, point_b, line_width = 1, color_line = (0,0,0)):
        self.cairo_ctx.move_to(self.scale * point_a[0], self.scale * point_a[1])
        #print ("int(point_b[0]), int(point_b[1])" , int(point_b[0]), int(point_b[1]))
        self.cairo_ctx.line_to(self.scale * point_b[0], self.scale * point_b[1])
        
        self.cairo_ctx.set_line_width(line_width)
        self.cairo_ctx.set_source_rgb(color_line[0], color_line[1], color_line[2])
        
        self.cairo_ctx.stroke()
        
    # Draws a line in the canvas from two points
    def draw_rectangle(self, vertex, line_width = 1, color_line = (0,0,0)):
        #self.cairo_ctx.move_to(int(point_a[0]), int(point_a[1]))
        #print ("int(point_b[0]), int(point_b[1])" , int(point_b[0]), int(point_b[1]))
        self.cairo_ctx.rectangle ( 0, 0, self.scale * vertex[0], self.scale * vertex[1])
        
        self.cairo_ctx.set_line_width(line_width)
        self.cairo_ctx.set_source_rgb(color_line[0], color_line[1], color_line[2])
        
        self.cairo_ctx.stroke()
        
    # Get the scale in relation with the two max parameters passed
    def get_scale(self, max_x, max_y):
        width = self.double_buffer.get_width()
        height = self.double_buffer.get_height()

        rel_h = width / max_x
        rel_v = height / max_y
        
        if rel_h > rel_v:      # The x dimension is the biggest
            scale = height / max_y
        elif rel_h < rel_v:    # The y dimension is the biggest
            scale = width / max_x
        else:                  # The x and y proportion are identical
            scale = height / max_y
            
        return scale
    
    # Sets the scale for the drawing
    def set_scale(self, scale):
        self.scale = scale


class Dialog_params(object):

    def __init__(self, object):
        self.load_parameters()
    
    def load_parameters(self):
        pass
        
        
        
class WindowGui(Gtk.ApplicationWindow):
    # a window
    def __init__(self, app):
        Gtk.Window.__init__(self, title="StatusBar", application=app)
        #self.set_default_size(200, 100)
    
        self.gladefile = "ui/builder_asimply_cnc.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        #self.builder.connect_signals({ "on_window_destroy" : Gtk.main_quit })
        self.window = self.builder.get_object("applicationwindow1")
        self.aboutdialog = self.builder.get_object("aboutdialog1")
        self.filechooserdialogopen = self.builder.get_object("filechooserdialogopen")
        self.filechooserdialogsave = self.builder.get_object("filechooserdialogsave")
        self.window_parameters = self.builder.get_object("dialog_preferences")
        self.dialog_edit_entity = self.builder.get_object("dialog_edit_entity")
        self.messagedialog = self.builder.get_object("messagedialog1")
        ##################self.canvas = Canvas()##############################################
        #self.canvas.add_events(Gdk.EventMask.BUTTON_PRESS_MASK) BUTTON_RELEASE)
        #self.canvas.connect('button-press-event', self.on_drawing_area_button_press)
        self.frame_canvas = self.builder.get_object("box4_canvas")
        self.canvas = Canvas()
        self.frame_canvas.pack_start(self.canvas, True, True, 0)
        ##################self.entities_list #################################################
        self.entities_list = self.builder.get_object("liststore3")
        self.entities_treeview = self.builder.get_object("treeview1")
        #self.entities_treeview.add_events(Gdk.EventType.BUTTON_RELEASE)
        #self.entities_treeview.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        #self.entities_treeview.connect('button-release-event', self.canvas.on_configure_event)
        ##################self.statusbar = Gtk.Statusbar()####################################
        self.statusbar = self.builder.get_object("statusbar1")
        # its context_id - not shown in the UI but needed to uniquely identify the source of a message
        self.context_id = self.statusbar.get_context_id("example")
        # we push a message onto the statusbar's stack
        self.statusbar.push(self.context_id, "Unkown status connection")
        self.textbuffer = self.builder.get_object("textbuffer1")
        self.window.show()
        
        #drawing.entities_list.subscribe(self.canvas.on_configure)
    
    ######################################################################################
    #### START -------------- self.entities_list ------------------------------ START ####
    ######################################################################################
        
    def on_configure_treeview(self):
        #Configure the double buffer based on size of the widget
        #self.entities_list.clear()
        if drawing.entities_list != []:
            self.populate(drawing.entities_list)
    
    # Toggles between selected or not in the diferent entities
    def on_toggle(self, widget, path):
        self.entities_list[path][2] = not self.entities_list[path][2]
        index = int (path)
        drawing.entities_list[index].select()
        #print (drawing.entities_list[index].selected, drawing.entities_list[index].name, drawing.entities_list[index].depth)
    
    # Allow changing the name of the entity     
    def name_edited(self, widget, path, name):
        self.entities_list[path][1] = name
        index = int (path)
        drawing.entities_list[index].name = name
    
    # Allow changing the depth of the entity     
    def depth_edited(self, widget, path, depth):
        self.entities_list[path][0] = float(depth)
        index = int (path)
        drawing.entities_list[index].depth = depth
    
    # Get the selected rows of the treeview and highlight the entities associated
    def get_selection_event(self, widget):
        self.get_selection()
        
    def get_selection(self):
        #model, rows = self.builder.get_object("treeview1").get_selection().get_selected_rows()
        model, rows = self.entities_treeview.get_selection().get_selected_rows()
        #model, rows = widget.get_selected_rows()
        self.canvas.queue_draw()
        if len(rows) < 1: #just return nothing if nothing is selected
            return None, None

        else: #pull titles and text out of the selected row and return
            # First unhighlight all
            for entity in drawing.entities_list:
                entity.highlighted = False
            # And now select highlight the selected
            for row in rows:
                index = int (row[0])
                drawing.entities_list[index].highlighted = not drawing.entities_list[index].highlighted
            
            return model, rows
    
    # Populate the list with the entities (another list)
    def populate(self, list):
        for entity in list:
            self.entities_list.append([entity.depth, entity.name, entity.selected ])
            
    def move_up_entity(self, widget):
        model, rows = self.get_selection()
        entities = drawing.entities_list
        
        if rows == None:
            print ("no entity selected")
            self.on_error_clicked("Error en edición", "No hay entidadades seleccionadas")
        else:
            for element in rows:
                index_row = int (element[0])
                if index_row != 0:
                    entities.insert(index_row-1, entities.pop(index_row))
        
                    itera = model.get_iter(index_row)
                    iterb = model.get_iter(index_row-1)
                    model.swap(itera, iterb)
                #name = model.get_value(itera,1)
    
    def move_down_entity(self, widget):
        model, rows = self.get_selection()
        entities = drawing.entities_list
        limit_down = len(entities)-1
        
        if rows == None:
            print ("no entity selected")
            self.on_error_clicked("Error en edición", "No hay entidadades seleccionadas")
        else:
            for element in rows:
                index_row = int (element[0])
                if index_row < limit_down:
                    entities.insert(index_row+1, entities.pop(index_row))
        
                    itera = model.get_iter(index_row)
                    iterb = model.get_iter(index_row+1)
                    model.swap(itera, iterb)
    
    def delete_entity(self, widget):
        model, rows = self.get_selection()
        entities = drawing.entities_list
        if rows == None:
            print ("no entity selected")
            self.on_error_clicked("Error en edición", "No hay entidadades seleccionadas")
        else:
            for element in rows:
                index_row = int (element[0])
                entities.pop(index_row)
                itera = model.get_iter(index_row)
                model.remove(itera)
    
    def update_entities(self, widget):
        """self.on_error_clicked("Sin acción", "Esta funcionalidad esta desactivada")
        return"""
        drawing.update_drawing()
        entities = drawing.entities_list
        """for entity in entities:
            print (entity.name, entity.depth, end=" ")
        print ("end")"""
    
    def edit_entity(self, widget):
        model, rows = self.get_selection()
        
        if rows == None:
            print ("no entity selected")
            self.on_error_clicked("Error en edición", "No hay entidadades seleccionadas")
        else:
            index_row = int (rows[0][0]) # Index of first selected entity
            self.putMessageLabel("entity_edit_depth", drawing.entities_list[index_row].depth)
            self.response = self.dialog_edit_entity.run()
            if self.response == 1: #Gtk.ResponseType.OK:
                self.edit_depth_entities(rows)
                print("The OK button was clicked")
            elif self.response == 2: #Gtk.ResponseType.CANCEL:
                print("The Cancel button was clicked")
            self.dialog_edit_entity.hide()
            
    ######################################################################################
    #### END -------------- self.entities_list ---------------------------------- END ####
    ######################################################################################
    
    ######################################################################################
    #### START ---------------- self.dialog_edit_entity ----------------------- START ####
    ######################################################################################
    
    def edit_depth_entities(self, rows):
        for element in rows:
            index_row = int (element[0])
            drawing.entities_list[index_row].depth = float(self.getLabelValue("entity_edit_depth"))
            self.entities_list[index_row][0] = drawing.entities_list[index_row].depth
    
    ######################################################################################
    #### END ------------------ self.dialog_edit_entity ------------------------- END ####
    ######################################################################################
    
    ######################################################################################
    #### START ---------------- self.window_parameters ------------------------ START ####
    ######################################################################################
    
    # Opens the parameters window
    def open_parameters_dialog(self, menuitem, data=None):
        self.populate_parameters()
        self.response = self.window_parameters.run()
        if self.response == 1: #Gtk.ResponseType.OK:
            self.parameters_get_from_dialog()
            print("The OK button was clicked")
        elif self.response == 2: #Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")
        self.window_parameters.hide()
    
    # Populates the entries with the parameters values
    def populate_parameters(self):
        self.putMessageLabel("vel_max", parameters.vel_max)
        self.putMessageLabel("steps_rev", parameters.steps_rev)
        self.putMessageLabel("dimX_max", parameters.dimX_max)
        self.putMessageLabel("dimY_max", parameters.dimY_max)
        self.putMessageLabel("dimZ_max", parameters.dimZ_max)
        self.putMessageLabel("ruta_arduino", parameters.ruta_arduino)
        self.putMessageLabel("baude_arduino", parameters.baude_arduino)
        self.putMessageLabel("placa_arduino", parameters.placa_arduino)
        self.putMessageLabel("max_dist", parameters.max_dist)
    
    # Sets the changes in the parameters values
    def parameters_get_from_dialog(self):
        parameters.vel_max = int(self.getLabelValue("vel_max"))
        parameters.steps_rev = int(self.getLabelValue("steps_rev"))
        parameters.dimX_max = float(self.getLabelValue("dimX_max"))
        parameters.dimY_max = float(self.getLabelValue("dimY_max"))
        parameters.dimZ_max = float(self.getLabelValue("dimZ_max"))
        parameters.ruta_arduino = self.getLabelValue("ruta_arduino")
        parameters.baude_arduino = self.getLabelValue("baude_arduino")
        parameters.placa_arduino = self.getLabelValue("placa_arduino")
        parameters.max_dist = float(self.getLabelValue("max_dist"))
        parameters.update_dict()
        
    # Get default parameters
    def parameters_default(self, widget):
        print ("hola")
        print (parameters.vel_max)
        parameters.return_default()
        self.populate_parameters()
        print (parameters.vel_max)
    
    # Save parameters in a file
    def parameters_save(self, widget):
        self.parameters_get_from_dialog()
        parameters.save_configuration()
        
    ######################################################################################
    #### END ------------------ self.window_parameters -------------------------- END ####
    ######################################################################################
    
    def on_gtk_about_activate(self, menuitem, data=None):        
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()
        
    def on_menu_file_quit(self, widget):
        Gtk.main_quit()
    def gtk_quit(self, *args):
        Gtk.main_quit(*args)
    #Destroy the file dialog open
    def on_filechooserdialogopen_destroy(self, widget, data=None):
        self.filechooserdialogopen.hide()
    #Destroy the file dialog save
    def on_filechooserdialogsave_destroy(self, widget, data=None):
        self.filechooserdialogsave.hide()
    
    def on_clear_status_activate(self, menuitem, data=None):
        print ("cleared status bar")
        self.statusbar.remove_message(0, self.message_id)

    def conectar(self, widget):
        arduino.conectar()
    def desconectar(self, widget):
        arduino.conectar()
    def reconectar(self, widget):
        arduino.conectar()
    def connection_check(self, widget):
        move.check()
        
    def button_move(self, widget):
        move.sendMove()
    
    def button_playCNC(self, button):
        if drawing.lista_coordenadas != []:
            move.playCNC()
        else:
            self.on_error_clicked("No hay coordenadas", "No hay coordenadas para enviar")
        
    def button_pauseCNC(self, button):
        move.pauseCNC()
        
    def button_stopCNC(self, button):
        move.stopCNC()
    
    def button_set_axis(self, button):
        move.new_zero()
    
    def button_move_0(self, button):
        move.sendToOrigin()
        
    def open_file(self, widget):
        drawing.load_from_file()
        
    def save_file(self, widget):
        drawing.save_draw_to_file()
        
    def clear_file(self, widget):
        drawing.delete_drawing()
        self.clearTextView()
        self.entities_list.clear()
        self.canvas.empty_canvas()
    
    def putMessageStatusBar(self, message):
        self.statusbar.push(self.context_id, message)
        
    def putMessageLabel(self, labelGui, message):
        self.label = self.builder.get_object(labelGui)
        self.label.set_text(str(message))
        
    def getLabelValue(self, labelGui):
        self.label = self.builder.get_object(labelGui)
        return self.label.get_text()
    
    def putTextTextView(self, textBufferGui, text):
        self.textbuffer = self.builder.get_object(textBufferGui)
        self.textbuffer.set_text(text)
        
    def insertTextTextView(self, textBufferGui, text):
        #self.textbuffer = self.builder.get_object(textBufferGui)
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.insert(end_iter, text)
    
    def getTextTextView(self, textViewGui):
        #self.textView = self.builder.get_object(textViewGui)
        #self.buffer = self.textView.get_buffer()
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        content = self.textbuffer.get_text(start_iter, end_iter, True)
        return content

    def clearTextView(self):
        start = self.textbuffer.get_start_iter()
        end = self.textbuffer.get_end_iter()
        self.textbuffer.delete(start, end)
    
    # Clear the canvas when the button is clicked
    def draw_clear(self, widget):
        print ("Clear button clicked")
        self.canvas.empty_canvas()
    
    # Updates the canvas when the button is clicked. Also from the cursor-changed event of the treeview (List of entities)
    def draw_update(self, widget, *kwargs):
        self.canvas.empty_canvas()
        if drawing.entities_list != []:
            self.canvas.on_configure()
        else:
            print ("No hay dibujo cargado")
        #self.draw_drawing(drawing.absolute_coords)
    
    # Calls the drawing into canvas function
    def button_draw_drawing(self, widget):
        if drawing.entities_list != []:
            drawing.draw_in_canvas()
        else:
            print ("No hay dibujo cargado")
            self.on_info_clicked( info_title="Archivo vacío", info_text="No hay dibujo cargado")
        #drawing.update_abs_coords(drawing.absolute_coords)
        #self.draw_drawing(drawing.absolute_coords)
        
            
    ######################################################################################
    #### START ------------------- self.messagedialog ------------------------- START ####
    ######################################################################################
    
    
    ##### Cambiar cada función por una que abra la ventana como el dialog_preferences, pero al final destroy()
    print ("###########Cambiar cada función por una que abra la ventana como el dialog_preferences, pero al final destroy()################")
    def on_info_clicked(self, info_title, info_text):
        dialog = Gtk.MessageDialog(self.messagedialog, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, info_title)#"This is an INFO MessageDialog")
        dialog.format_secondary_text(info_text)
        dialog.run()
        print("INFO dialog closed")

        dialog.destroy()
    
    def on_error_clicked(self, error_title, error_text):
        dialog = Gtk.MessageDialog(self.messagedialog, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CANCEL, error_title)
        dialog.format_secondary_text(error_text)
        dialog.run()
        print("ERROR dialog closed")

        dialog.destroy()

    def on_warn_clicked(self, widget):
        dialog = Gtk.MessageDialog(self.messagedialog, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK_CANCEL, "This is an WARNING MessageDialog")
        dialog.format_secondary_text(
            "And this is the secondary text that explains things.")
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("WARN dialog closed by clicking OK button")
        elif response == Gtk.ResponseType.CANCEL:
            print("WARN dialog closed by clicking CANCEL button")

        dialog.destroy()

    def on_question_clicked(self, widget):
        dialog = Gtk.MessageDialog(self.messagedialog, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "This is an QUESTION MessageDialog")
        dialog.format_secondary_text(
            "And this is the secondary text that explains things.")
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            print("QUESTION dialog closed by clicking YES button")
        elif response == Gtk.ResponseType.NO:
            print("QUESTION dialog closed by clicking NO button")

        dialog.destroy()
    
    ######################################################################################
    #### END --------------------- self.messagedialog --------------------------- END ####
    ######################################################################################


# Variables de preferencias
paramOpened = 1          #Variable que almacena si se ha abierto la ventana de parametros

# Iniciar algunas funciones
posicion = comm.Position()

parameters = files.Parameters()
# Inicia la conexion con la maquina
arduino = comm.Machine (parameters.ruta_arduino, parameters.baude_arduino)
if arduino.connected:
    print("arduino connected")
else:
    print ("arduino disconnected")

print ("parameters.ruta_arduino, parameters.baude_arduino", parameters.ruta_arduino, parameters.baude_arduino)
#arduino = comm.Machine ("/dev/ttyACM0", 19200)

# Initiate the drawing
worktable = comm.Worktable(parameters.dimX_max, parameters.dimY_max, parameters.dimZ_max)
drawing = comm.Drawing()

# Initiate the move object
move = comm.Move_instructions()

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        self.win = WindowGui(self)
        #win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

if __name__ == "__main__":
    GObject.threads_init() # Deprecated use
    app = MyApplication()
    app.run(sys.argv)

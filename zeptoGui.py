import PySimpleGUI as sg
import datetime
import time
import serial
import io
import codecs

serial_port = 'COM6'
gap_pos_limit = 180
gap_neg_limit = 0.5
cen_pos_limit = 10.0
cen_neg_limit = -10.0

# Create the layout
layout = [[sg.Text('Gap_RBV: '), sg.Text('', key='_gap_', size=(20, 1))],
         [sg.Text('Centre_RBV: '), sg.Text('', key='_centre_', size=(20, 1))],
         [sg.Text('Gap_DMD: '), sg.InputText(gap_pos_limit) ],
         [sg.Text('Centre_DMD: '),sg.InputText('0')],
         [sg.Button('GO'), sg.Button('STOP'), sg.Quit()]]

# Create the window object
window = sg.Window('Simple Clock').Layout(layout)


def getTime():
    return datetime.datetime.now().strftime('%H:%M:%S')
    
def getQVar(port,var):
    #Flush
    port.reset_input_buffer()
    port.write(f'&2 Q{var}\r\n'.encode())
    port.flush()
    response = port.read_until(b'\r')
    
    #Flush
    port.reset_input_buffer()
    return float(response.strip(b'\x06'))
    
def executeMove(port,gap,cen):

    if gap > gap_pos_limit:
        gap = gap_pos_limit
    if gap < gap_neg_limit:
        gap = gap_neg_limit
    if cen > cen_pos_limit:
        cen = cen_pos_limit
    if cen < cen_neg_limit:
        cen = cen_neg_limit
        
    port.write(f'&2 Q78 = {gap}\r\n'.encode())
    port.flush()
    port.write(f'&2 Q77 = {cen}\r\n'.encode())
    port.flush()
    port.write(b'&2a\r\n')
    port.flush()
    port.write(b'&2b10r\r\n')
    port.flush()
    port.reset_input_buffer()
    
    
    
def main(gui_obj):
    
    ser = serial.Serial(serial_port)  # open serial port
    ser.baudrate = 38400
    synced = False
    # Event loop
    while True:
        event, values = gui_obj.Read(timeout=10)
            
        time.sleep(0.1)
        # Exits program cleanly if user clicks "X" or "Quit" buttons
        if event in (None,'Quit'):
            break
        if event == 'GO':
            if values[0].isnumeric() and values[1].isnumeric() :
                executeMove(ser,float(values[0]),float(values[1]))
            else:
                print("Invalid demand value\r")
        if event == 'STOP':
            ser.write(b'&2a\r\n')
            ser.flush()
            ser.reset_input_buffer()

        # Update '_time_' key value with return value of getTime()
        gui_obj.FindElement('_gap_').Update(getQVar(ser,88))
        gui_obj.FindElement('_centre_').Update(getQVar(ser,87))

if __name__ == '__main__':
    main(window)
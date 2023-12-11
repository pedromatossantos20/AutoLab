import pyvisa
import pandas as pd

def recognize_setup(): #associates a setup name to an adress OR IDN name
    df_setups = pd.DataFrame({
            "Setup_Name": ["KEITHLEY 2401", "KEPCO", "KEPCO", "HP6032A"],
            "Nadress": ["?", "?", "?", "?"],
            "IDN_RESPONSE": ["?", "?", "?", "?"],
            "Type": ["Sourcemeter", "Magnetic coil", "Magnetic coil", "Magnetic coil"],
            "Nickname": ["2K Sourcemeter", "400 Oe Coils", "140 Oe Coils", "2K Coils"]
        })
    
    rm=pyvisa.ResourceManager()
    list_adresses_available=list(rm.list_resources())

    #print(list_adresses_available)

    list_adresses_available_filtered=[string for string in list_adresses_available if "GPIB" in string]
    list_adresses_available=list_adresses_available_filtered

    df_available_setups=pd.DataFrame(columns=["Setup_Name","GPIB_ADDRESS","IDN_RESPONSE","Type","Nickname"])

    df_available_setups["Setup_Name"] = df_setups["Setup_Name"]
    df_available_setups['Type'] = df_setups['Type']
    df_available_setups['Nickname'] = df_setups['Nickname']

  
    for adress in list_adresses_available:
       
        inst = rm.open_resource(adress)
        idn_name = inst.query("*IDN?")
        if(idn_name == '\n'):
            idn_name = inst.query("ID?")

        #print(idn_name)
        inst.close()

        match =False

        for setup_name in df_setups["Setup_Name"]:
            if all(word in idn_name for word in setup_name.split(" ") ):
                match=True
                df_available_setups.loc[df_available_setups["Setup_Name"] == setup_name, 'IDN_RESPONSE'] = idn_name
                df_available_setups.loc[df_available_setups["Setup_Name"] == setup_name, 'GPIB_ADDRESS'] = adress
        
        for Nadress in df_setups["Nadress"]:
            if str(Nadress) in adress:
                match=True
                name=df_setups[df_setups["Nadress"] == Nadress]["Setup_Name"].iloc[0]
                df_available_setups.loc[df_available_setups["Setup_Name"] == name, 'GPIB_ADDRESS'] = adress
    
        if match==False:
            new_row={"Setup_Name" : "Not Recognized", "GPIB_ADDRESS": adress, "IDN_RESPONSE":idn_name}
            #df_available_setups = pd.concat([df_available_setups,new_row],ignore_index=True)
            new_row_df = pd.DataFrame([new_row])  # Convert new_row to a DataFrame
            df_available_setups = pd.concat([df_available_setups, new_row_df], ignore_index=True)


    #rm.close()
    return df_available_setups

################################################################################################################################################################################################
import pyvisa

class External_Instrument():
    def __init__(self, name=None, inst_address=None, term_chars=None, baud_rate=None, timeout=None):
        self.name = name
        
        rm = pyvisa.ResourceManager()
        self.gpib = rm.open_resource(inst_address)
        
        self.gpib.write_termination = term_chars
        self.gpib.read_termination = term_chars
        self.gpib.baud_rate = baud_rate
        self.gpib.timeout = timeout
##################################################################################################################################################################################
import time

class SourceMeter(External_Instrument):
    def __init__(self,
                  name ,
                  inst_address,
                  baud_rate = 9600,
                  term_chars = '\n',
                  timeout = 3000,**kwargs):
            
        
        super().__init__(name = name,
                  inst_address = inst_address,
                  baud_rate = baud_rate,
                  term_chars = term_chars,
                  timeout = timeout)
        
        if self.name == "KEITHLEY 2401":
            self.filter_list=["REP","MOV"]
            self.set_sourcing_mode(mode="CURR")
            self.set_measurement_functions(functions=["VOLT"])
            self.set_measurement_speed()
            self.auto_range_source()
            self.set_measurment_voltage_range()
            self.set_measurment_current_range() #auto measure_func
            
            self.set_current(0)
            self.set_voltage_compliance(1)
            self.set_output_mode()
            self.set_filter(filter="REP")
            self.set_filter_count(10)
            self.set_data_elements(elements=["VOLT","CURR", "RES", "TIME", "STAT"])
            self.triad(base_frequency=3500,duration=1),
        

        else:
            self.filter_list=["NONE"]
            
    def set_sourcing_mode(self,mode="CURR"): 
        if self.name == "KEITHLEY 2401":#pg 378
            if(mode != "CURR" and mode != "VOLT"):
                error_message = "The mode chosen for " + self.name + " must be CURR or VOLT. " + mode + " is not a valid mode"
                return error_message
            else:
                self.mode=mode
                self.gpib.write(":SOUR:FUNC " + mode)
                #self.gpib.write(":SOUR:" + str(mode) + ":RANG:AUTO 1")


    def set_voltage_compliance(self,voltage):
        if self.name == "KEITHLEY 2401": #pg 372
            if voltage > -21 and voltage<21:
                self.gpib.write(":SENS:VOLT:PROT " + str(voltage))
        
    
    def set_current_compliance(self,current):
        if self.name == "KEITHLEY 2401": #pg 372
            if current > -0.2 and current<0.2:
                self.gpib.write(":SENS:CURR:PROT " + str(current))
    
    def read_compliance_state(self,element):
        if self.name == "KEITHLEY 2401": #pg 372
            state=self.gpib.query(":SENS:"+  str(element) + ":PROT:TRIP?")
            return state
    
    def set_measurement_speed(self, time=17e-3): #NPL cycles
        if self.name == "KEITHLEY 2401": #pg 374
            cycles=round(time,2)*60
            self.gpib.write(":SENS:CURR:NPLCycles " + str(cycles))
    
        
    def set_measurment_current_range(self,range="AUTO"):
        if range!= "AUTO":
            self.gpib.write(":SENS:CURR:RANG " + str(range) )
        else:
            self.gpib.write(":SENS:CURR:RANG:AUTO 1" )

    def set_measurment_voltage_range(self,range="AUTO"):
        if range!= "AUTO":
            self.gpib.write(":SENS:VOLT:RANG " + str(range) )
        else:
            self.gpib.write(":SENS:CURR:RANG:AUTO 1" )

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        if self.mode == 'CURR':
            self.gpib.write(":SOUR:CURR:RANG:AUTO 1")
        else:
            self.gpib.write(":SOUR:VOLT:RANG:AUTO 1")

    def set_current(self,current): #only valid if in CURR mode pg382
        if self.name == "KEITHLEY 2401":
            self.gpib.write(":SOUR:CURR:LEV "+str(current))


    def set_voltage(self,voltage): #pg382
        if self.name == "KEITHLEY 2401":
            self.gpib.write(":SOUR:VOLT:LEV "+str(voltage))
    
    def set_filter_count(self,count):#pg375
        if self.name == "KEITHLEY 2401":
            self.gpib.write(":SENS:AVER:COUN "+str(count))
    
    def set_filter(self,filter):#pg375
        if self.name == "KEITHLEY 2401":
            self.gpib.write(":SENS:AVER:TCON "+str(filter))
    
    def set_source_delay(self,delay):#pg387 set delay to stabilize source (Can be auto)
        if self.name == "KEITHLEY 2401":
            if delay != "AUTO":
                delay = round(delay,4)
                self.gpib.write(":SOUR:DEL:AUTO 0")
                #time.sleep(0.1)
                self.gpib.write(":SOUR:DEL "+str(delay))
            else:
                self.gpib.write(":SOUR:DEL:AUTO 1")
    
    def set_output_mode(self,mode = "AUTO"):#pg 377
        if self.name == "KEITHLEY 2401":
            if mode != "AUTO":
                self.gpib.write(":SOUR:CLE:AUTO:MODE ", mode)
            else:
                self.gpib.write(":SOUR:CLE:AUTO 1")
    
    def set_data_elements(self, elements): #pg354
        if self.name == "KEITHLEY 2401":
            string_elements=":FORM:ELEM " + elements[0]
            valid_elements = ["VOLT","CURR", "RES", "TIME", "STAT"]
            for element in elements[1:]:
                if element not in valid_elements:
                    error_message = "The element chosen for " + self.name + " must be " + str(valid_elements) + " ." + element + " is not a valid element"
                    return error_message
            
                string_elements=string_elements + ", " + element
            self.data_elements = elements 
            print(string_elements)
            self.gpib.write(string_elements)  
                   

    def read(self,element):
        if self.name == "KEITHLEY 2401":
            measurment_data = self.gpib.query(":READ?")
            measurment_data=measurment_data.split(",")
            index=self.data_elements.index(element)
            return float(measurment_data[index])
    
    def set_measurement_functions(self,functions):
        if self.name == "KEITHLEY 2401":
            self.gpib.write(":SENS:FUNC:CONC 1")

            string_functions=":FUNC"
            valid_functions = ["VOLT","CURR", "RES"]
            for function in functions:
                if function not in valid_functions:
                    error_message = "The function chosen for " + self.name + " must be " + str(valid_functions) + " ." + function + " is not a valid function"
                    return error_message
            
                string_functions=string_functions + " '" + function + "' ,"
                
            string_functions=string_functions.rstrip(string_functions[-3:]) + "'"
            self.measurement_functions = functions 
            print(string_functions)
            self.gpib.write(string_functions)  

    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.gpib.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)
    
    def symphony(self, base_frequency, duration, times):
        for i in range(1,times):
            self.beep(base_frequency*(4.0+i)/4.0, duration)
            time.sleep(duration)

        
    
    
################################################################################################################################################################################
#pg47 and 80
#pg47 and 80
#pg47 and 80
#pg47 and 80
import time
import serial
import pandas as pd
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display, clear_output

class Magnetic_Coils(External_Instrument):
    def __init__(self,
                  name ,
                  inst_address,
                  baud_rate = 9600,
                  term_chars = '\r\n',
                  timeout = 2000, **kwargs):
        
        
        super().__init__(name = name,
                  inst_address = inst_address,
                  baud_rate = baud_rate,
                  term_chars = term_chars,
                  timeout = timeout)
        
        if name=="KEPCO":
            self.stab_time=1
            if kwargs.get("setup") == "140 Oe Coils":
                self.K=4/140
                self.stab_time=2
            else:
                self.K=1.385/401
            self.set_operating_mode("CURR")
            self.output_state("ON")
            self.set_current(0)
            self.set_voltage(50)
            self.arduino=False
            
        if name=="HP6032A":
            self.last_field=None
            self.Imax=18
            self.stab_time=0

            self.K=17.6/1900
            self.output_state("ON")
            self.set_voltage(50)
            self.check_period= 0.5
            self.accuracy=0.015
            self.current_inverted=False
            
            arduino_port=kwargs.get("arduino_port")
            self.arduino = serial.Serial(arduino_port, 9600)
            time.sleep(2)  # Wait for the Arduino to initialize
            self.set_polarity_invertor(False)
            
            self.calibration("POS")
            self.calibration("NEG")
            self.set_current(0)



    def check_direction(self,field):
        
        if self.last_field==None:
            if (field>0):
                self.last_field = 2000
                self.set_current(self.Imax,accuracy=0.2)
                self.direction="NEG"
        
            else:
                self.last_field = - 2000
                self.set_current(- self.Imax,accuracy=0.2)
                self.direction="POS"
        else:
            if(field - self.last_field>0):
                if(self.direction != "POS"):
                    self.set_current(-self.Imax,accuracy=0.2)

                self.direction="POS"

            elif(field - self.last_field<0):
                if(self.direction != "NEG"):
                    self.set_current(self.Imax,accuracy=0.2)
                    
                
                self.direction="NEG"
            
            self.last_field = field
            

        if (self.direction=="NEG"):
            self.current_interpolation = self.current_interpolation_neg

        elif (self.direction=="POS"):
            self.current_interpolation = self.current_interpolation_pos
        
        

        return(self.direction)


    def set_magnetic_field(self,field):
        if self.name == "KEPCO":
            current=self.K*field
            self.set_current(current)
            return current
        
        if self.name == "HP6032A":

            self.check_direction(field)
            current=self.current_interpolation(field)
            self.set_current(current)
                
            return current
        
    
    def set_operating_mode(self,mode="CURR"):
        if self.name == "KEPCO":                      #pg47 and 80
            if(mode != "CURR" and mode != "VOLT"):
                error_message = "The mode chosen for " + self.name + " must be CURR or VOLT. " + mode + " is not a valid mode"
                return error_message
            self.mode=mode
            self.gpib.write("FUNC:MODE " + str(mode))
        

    def set_current(self,current,accuracy=None): #if in VOLT mode sets current limit 
        
        if self.name == "KEPCO":          
            if(current<0):
                self.set_voltage(-50)
            else:
                self.set_voltage(50)
            self.gpib.write("SOUR:CURR " + str(current))
            time.sleep(self.stab_time)

        if self.name == "HP6032A":
            if accuracy==None:
                 accuracy=self.accuracy

            if(current<0):
                self.set_polarity_invertor(bool=True)
                current=-current
            elif(current>0):
                self.set_polarity_invertor(bool=False)

            
            self.gpib.write("ISET " + str(current))

            time.sleep(self.stab_time)
            flag=False
            while flag == False:
                current_real = self.read_current()
                #print(current_real-current)
                if abs(current_real -current)<accuracy:
                    flag=True
                    return 1
                time.sleep(self.check_period)
        return 1
    
    def set_polarity_invertor(self,bool=False):
        if(self.current_inverted!=bool):
            self.set_current(0,accuracy=0.3)


        if (bool==True):
            self.arduino.write(b'111')
            self.current_inverted=bool
        elif(bool==False):
            self.arduino.write(b'000')
            self.current_inverted=bool


        return self.current_inverted
    
    def read_current(self):
        if self.name == "KEPCO":
            current=self.gpib.query("MEAS:CURR?")
        if self.name == "HP6032A":
            current=self.gpib.query("IOUT?")
        return float(current.split()[-1])
    
    def read_voltage(self):
        if self.name == "KEPCO":
            voltage=self.gpib.query("MEAS:VOLT?")
        if self.name == "HP6032A":
            voltage=self.gpib.query("VOUT?")
        return voltage
    
    def set_voltage(self, voltage): #if in CURR mode sets volt limit
        if self.name == "KEPCO":
            self.gpib.write("SOUR:VOLT " + str(voltage))
        if self.name == "HP6032A":
            self.gpib.write("VSET " + str(voltage))
            
        return 1
    
    def output_state(self,state):
        if self.name == "KEPCO":
            if(state != "ON" and state != "OFF"):
                error_message = "The State Chosen for " + self.name + " must be ON or OFF. " + state + " is not a valid state"
                return error_message
            
            self.gpib.write("OUTP " + state)
        if self.name == "HP6032A":
            self.gpib.write("OUT " + state)
            
            return (1)
    
    
    def gather_calibration_data(self, direction,accuracy,I_list,save_file=None):
        if save_file is None:
            save_file = self.name + "_CalibrationData_" + direction

        Calibration_Data = []

        # Initialize the plot
        fig, ax = plt.subplots()

        for I in I_list:
            self.set_current(I,accuracy=accuracy)
            # Get H from user input
            H = float(input(f"Enter the value of H for current I = {I}: "))
            Calibration_Data.append([self.name, I, H])

            # Update the DataFrame and plot
            df = pd.DataFrame(Calibration_Data, columns=['Name', 'I[A]', 'H[Oe]'])

            # Update plot
            ax.clear()
            df = pd.DataFrame(Calibration_Data, columns=['Name','I[A]', 'H[Oe]'])
            ax.scatter(df['I[A]'], df['H[Oe]'])
            ax.set_xlabel('I[A]')
            ax.set_ylabel('H[Oe]')
            ax.set_title('Real-Time Calibration Data')
            
            display(fig)
            clear_output(wait=True)  # Clear the previous plot and input

        # Save the DataFrame to a CSV file
        Calibration_Data = pd.DataFrame(Calibration_Data, columns=['Name', 'I[A]', 'H[Oe]'])
        Calibration_Data.to_csv(save_file + ".csv")

        # Save the plot to a file
        plt.savefig(save_file + "_plot.png")
        plt.show()

        return Calibration_Data
    def gather_calibration_data_auto(self, direction,accuracy,I_list,save_file=None):
        if save_file is None:
            save_file = self.name + "_CalibrationData_" + direction

        Calibration_Data = []

        # Initialize the plot
        fig, ax = plt.subplots()
        
        self.init_gaussemeter()
        
        for I in I_list:
            self.set_current(I,accuracy=accuracy)
            # Get H from user input
            H = self.gaussmeter_read()

            Calibration_Data.append([self.name, I, H])

            # Update the DataFrame and plot
            df = pd.DataFrame(Calibration_Data, columns=['Name', 'I[A]', 'H[Oe]'])

            # Update plot
            ax.clear()
            df = pd.DataFrame(Calibration_Data, columns=['Name','I[A]', 'H[Oe]'])
            ax.scatter(df['I[A]'], df['H[Oe]'])
            ax.set_xlabel('I[A]')
            ax.set_ylabel('H[Oe]')
            ax.set_title('Real-Time Calibration Data')
            
            display(fig)
            clear_output(wait=True)  # Clear the previous plot and input

        # Save the DataFrame to a CSV file
        Calibration_Data = pd.DataFrame(Calibration_Data, columns=['Name', 'I[A]', 'H[Oe]'])
        Calibration_Data.to_csv(save_file + ".csv")

        # Save the plot to a file
        plt.savefig(save_file + "_plot.png")
        plt.show()

        return Calibration_Data
    
    def calibration(self, direction, calibration_file=None, plot=False):
        if calibration_file is None:
            calibration_file = self.name + "_CalibrationData_" + direction

        try:
            # Read the calibration data
            df = pd.read_csv(calibration_file + ".csv")
            #print(df)
            
            # Extract I and H data
            I = df['I[A]']
            H = df['H[Oe]']

            # Generate the interpolation function (interpolate I as a function of H)
            interp_function = interp1d(H, I, kind='cubic', fill_value='extrapolate')

            if plot:
                # Create a set of H values for plotting the interpolation function
                H_values_for_plot = np.linspace(min(H), max(H), 500)

                # Use the interpolation function to predict I for these H values
                I_values_for_plot = interp_function(H_values_for_plot)

                # Plot the experimental data
                plt.scatter(H, I, label='Experimental Data', color='red')

                # Plot the interpolation function
                plt.plot(H_values_for_plot, I_values_for_plot, label='Interpolation', color='blue')

                # Add labels and title
                plt.ylabel('I[A]')
                plt.xlabel('H[Oe]')
                plt.title('Interpolation vs Experimental Data')
                plt.legend()

                # Show the plot
                plt.show()

            if (direction=="POS"):
                self.current_interpolation_pos = interp_function 
            if (direction=="NEG"):
                self.current_interpolation_neg = interp_function

            return interp_function
        except FileNotFoundError:
            print(f"The file {calibration_file} was not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def init_gaussemeter(self,com="COM8"):
        gaussemeter = serial.Serial(com, baudrate=57600, timeout=0.2,bytesize=7,parity=serial.PARITY_ODD)
        self.gaussemeter=gaussemeter
        gaussemeter.write(b'AUTO\r\n')
        a=gaussemeter.read_until((b'\r\n').decode('ascii'))
    
    def gaussmeter_read(self):
        time.sleep(1)
        self.gaussemeter.write(b'RDGFIELD?\r\n')
        H=self.gaussemeter.read_until((b'\r\n').decode('ascii'))
        str_data = H.decode('utf-8').strip()

        return float(str_data)


        
    
    


        
    
    


########################################################################################################################################
  
    

        
    
    

        
    
    
        

        
    
    
        

        
    
    

        
    
    

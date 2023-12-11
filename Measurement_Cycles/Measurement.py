import pandas as pd
import numpy as np
import datetime
import time

class MeasurmentObject():
    def __init__(self,**kwargs):

        self.measurement_recipe=kwargs.get("measurement_recipe")
        
        self.channel_list=kwargs.get("channel_list")
        self.available_pins=kwargs.get("available_pins")
        self.current_source=kwargs.get("current_source")
        self.voltimeter=kwargs.get("voltimeter")
        self.magnet=kwargs.get("magnet")

        
        self.multiplexer=kwargs.get("pcb_cannon")

        self.pins_with_sensors=kwargs.get("pins_with_sensors")

        self.save_file=kwargs.get("save_file")
        if self.save_file==None:
            self.save_file="save_file"
        self.goniometer=kwargs.get("goniometer")

        metadata=kwargs.get("metadata")
        self.metadata = metadata if metadata is not None else {}

           
    
    def map_sensor_to_pin(self,current=1e-5,voltage_compliance=10):
        channel1=self.channel_list[0]
        channel2=self.channel_list[1]

        pins_with_sensors=[]
        combination=0

        self.current_source.set_current(current)
        self.voltimeter.set_voltage_compliance(voltage_compliance)
        limit=voltage_compliance*0.95

        for pin1 in range(1,self.available_pins+1):
            self.multiplexer.set_channel_to_pin(channel1,pin1)
            for pin2 in range(1,self.available_pins+1):
                if pin1<=pin2:
                    continue
                
                self.multiplexer.set_channel_to_pin(channel2,pin2)
                measurment_data=self.voltimeter.read("VOLT")
          
                if measurment_data<limit:
                    pins_with_sensors.append([pin1,pin2])
        
        self.pins_with_sensors=pins_with_sensors


        return pins_with_sensors
                    
class Current_Source_2PP(MeasurmentObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.H_list=kwargs.get("H_list")
        self.current=kwargs.get("current")
        self.voltage_compliance=kwargs.get("voltage_compliance")
        self.angle_list=kwargs.get("angle_list")
        self.measurement()
    

    def measurement(self):
        channel1=self.channel_list[0]
        channel2=self.channel_list[1]

        if self.pins_with_sensors==None:
            self.map_sensor_to_pin(current=self.current,voltage_compliance=self.voltage_compliance)
        self.pins_with_sensors=[[1,2],[2,4]]
        

        self.current_source.set_current(self.current)
        self.voltimeter.set_voltage_compliance(self.voltage_compliance)

        Measurement_Data=[]

        for H in self.H_list:
            magnet_current=self.magnet.set_magnetic_field(H)
            self.current_source.triad(base_frequency=1500,duration=0.05)

            for sensor in self.pins_with_sensors:#
                pin1=sensor[0]
                pin2=sensor[1]
                self.multiplexer.set_channel_to_pin(channel1,pin1)
                self.multiplexer.set_channel_to_pin(channel2,pin2)

                measurment=self.voltimeter.read("VOLT")
                now = datetime.datetime.now()
                Measurement_Data.append([sensor,H, self.current, measurment,measurment/self.current,magnet_current,now])
            
        self.magnet.set_magnetic_field(0)
        

        self.Measurement_Data = pd.DataFrame(Measurement_Data,columns=['Pins','H[Oe]', 'I[A]', 'V[V]', 'R[Ohms]','Magnet Current(A)','Date'])

        for key, value in self.metadata.items():
            self.Measurement_Data[key] = value

        self.Measurement_Data.to_csv(self.save_file + ".csv")
        self.Measurement_Data.to_csv(self.save_file+'.txt', sep='\t', index=False)
        self.multiplexer.close()
                
        if self.magnet.arduino!=False:
             self.magnet.arduino.close()


        self.current_source.triad(base_frequency=2000,duration=0.5)

        
        return self.Measurement_Data

class Beatriz_likes_acid(MeasurmentObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.H_list=kwargs.get("H_list")
        self.current=kwargs.get("current")
        self.voltage_compliance=kwargs.get("voltage_compliance")
        self.measurement_time= 2.5*60*60       #kwargs.get("measurement_time")
        self.rest_time= 0                       #kwargs.get("rest_time")
        self.measurement()
    

    def measurement(self):
        channel1=self.channel_list[0]
        channel2=self.channel_list[1]

        if self.pins_with_sensors==None:
            self.map_sensor_to_pin(current=self.current,voltage_compliance=self.voltage_compliance)

        self.current_source.set_current(self.current)
        self.voltimeter.set_voltage_compliance(self.voltage_compliance)

        Measurement_Data=[]
        
        start_time=time.time()

        self.current_source.symphony(base_frequency=1000,duration=0.5,times=10)

        while (time.time()-start_time<self.measurement_time):
            for H in self.H_list:
                magnet_current=self.magnet.set_magnetic_field(H)
                #self.current_source.triad(base_frequency=1500,duration=0.05)

                for sensor in self.pins_with_sensors:#
                    pin1=sensor[0]
                    pin2=sensor[1]
                    self.multiplexer.set_channel_to_pin(channel1,pin1)
                    self.multiplexer.set_channel_to_pin(channel2,pin2)

                    measurment=self.voltimeter.read("VOLT")
                    now = datetime.datetime.now()
                    Measurement_Data.append([sensor,H, self.current, measurment,measurment/self.current,magnet_current,now])
            time.sleep(self.rest_time)
            self.current_source.triad(base_frequency=2500,duration=0.5)


            
        self.magnet.set_magnetic_field(0)
        

        self.Measurement_Data = pd.DataFrame(Measurement_Data,columns=['Pins','H[Oe]', 'I[A]', 'V[V]', 'R[Ohms]','Magnet Current(A)','Date'])

        for key, value in self.metadata.items():
            self.Measurement_Data[key] = value

        self.Measurement_Data.to_csv(self.save_file + ".csv")
        self.Measurement_Data.to_csv(self.save_file+'.txt', sep='\t', index=False)
        self.multiplexer.close()
                
        if self.magnet.arduino!=False:
             self.magnet.arduino.close()

        self.current_source.symphony(base_frequency=1000,duration=0.5,times=10)
        

        
        return self.Measurement_Data

    
class Current_Source_Angular_2PP(MeasurmentObject):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.H_list=kwargs.get("H_list")
        self.current=kwargs.get("current")
        self.voltage_compliance=kwargs.get("voltage_compliance")
        self.angle_list=kwargs.get("angle_list")
        self.measurement()

    
    def measurement(self):
        channel1=self.channel_list[0]
        channel2=self.channel_list[1]

        if self.pins_with_sensors==None:
            self.pins_with_sensors = self.map_sensor_to_pin(current=self.current,voltage_compliance=self.voltage_compliance)
        self.pins_with_sensors=[[1,2],[2,4]]
        self.current_source.set_current(self.current)
        self.voltimeter.set_voltage_compliance(self.voltage_compliance)

        

        Measurement_Data=[]

        default_accuracy=self.magnet.accuracy

        for H in self.H_list:
            magnet_current=self.magnet.set_magnetic_field(H)
            self.current_source.triad(base_frequency=1500,duration=0.05)
            #print(self.angle_list)
            for angle in self.angle_list:
                
                if self.goniometer!=False:
                    self.goniometer.set_angle(float(angle))
                    if(angle == self.angle_list[0]):
                        self.magnet.accuracy=default_accuracy
                        magnet_current=self.magnet.set_magnetic_field(H)

                for sensor in self.pins_with_sensors:#
                    pin1=sensor[0]
                    pin2=sensor[1]
                    self.multiplexer.set_channel_to_pin(channel1,pin1)
                    self.multiplexer.set_channel_to_pin(channel2,pin2)

                    measurment=self.voltimeter.read("VOLT")
                    now = datetime.datetime.now()
                    Measurement_Data.append([sensor,H, self.current, measurment,measurment/self.current,magnet_current,angle,now])
            
            if self.goniometer!=False:
                self.magnet.accuracy=100

        self.magnet.set_magnetic_field(0)
        

        self.Measurement_Data = pd.DataFrame(Measurement_Data,columns=['Pins','H[Oe]', 'I[A]', 'V[V]', 'R[Ohms]','Magnet Current(A)','Measurement_Angle','Date'])

        for key, value in self.metadata.items():
            self.Measurement_Data[key] = value

        self.Measurement_Data.to_csv(self.save_file + ".csv")
        #self.Measurment_Data.to_excel(self.save_file + ".xlsx")
        self.Measurement_Data.to_csv(self.save_file+'.txt', sep='\t', index=False)
        
        self.multiplexer.close()
        if self.magnet.arduino!=False:
             self.magnet.arduino.close()

        self.current_source.triad(base_frequency=2000,duration=0.5)

        
        return self.Measurement_Data

    






             
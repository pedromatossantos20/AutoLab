# Automation Software for Electrical Characterization in Varying Magnetic Fields

## Project Overview

This software suite was developed as part of my master's thesis and is designed to automate the process of electrical characterization in varying magnetic fields. It integrates a custom-built device for measuring magnetic sensors in parallel, enhancing efficiency compared to traditional sequential methods. The software effectively interfaces with existing laboratory equipment, creating a unified framework for diverse characterization tasks.

## Key Features

- **Comprehensive Control**: The software provides control over various instruments, including sourcemeters, current sources, goniometers, current polarizers, and the custom-built magnetic sensor measurement device.
- **Flexible Measurement Recipes**: Includes a user-friendly interface for creating and executing measurement recipes. These leverage the capabilities of the built device, enabling streamlined and precise measurement procedures.
- **Modular Architecture**: Designed with a flexible architecture that facilitates communication across different experimental setups using uniform commands. This means the software remains compatible with new or alternate setups; users simply need to integrate the specific commands of new instruments into the "External_Instruments.py" file (see examples in that file).
- **Customization and Abstraction**: The architecture supports easy modification and creation of new measurement procedures. It abstracts the complexities of the individual instruments, allowing users to focus on the experimental design without delving into the specificities of each piece of equipment.

The aim is to provide a robust, adaptable, and user-friendly tool for researchers and professionals engaged in electrical characterization in magnetic fields, ensuring efficient and accurate data collection and analysis.


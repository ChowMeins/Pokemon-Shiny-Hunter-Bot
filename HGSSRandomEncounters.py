import globals as g
import time

def readSensor() -> int:
    g.ser.write(b'light\n')
    light = g.ser.readline().decode('ASCII').strip()
    #print(light)
    return int(light)

def sendCommand(ser, command, delay):
    ser.write(f'{command}'.encode('utf-8'))
    time.sleep(delay)

def compareLight(start: int, bound: int) -> bool:
    curr = readSensor()
    #print(f"Start light level: {start}, Current light level: {curr}")
    if (curr in range(start - bound, start + bound)):
        return False
    return True
def runAway(): # Executes run away sequence
    sendCommand(g.ser, 'l\n' , 0.75)
    sendCommand(g.ser, 'l\n', 0.75)
    sendCommand(g.ser, 'r\n', 0.75)
    sendCommand(g.ser, 'a1000\n', 0.75)
    sendCommand(g.ser, 'a\n', 2)

def HGSSRandomEncounters():

    tileCount = input("Enter the number of tiles of grass from left to right.\n")
    delay = str(125 * int(tileCount))
    encounters = 0
    encounterDuration = None
    shinyFound = False
    average = 0
    totalDuration = 0

    # Execute while loop
    while not g.stop_threads:
        time.sleep(1)
        startLightVal = readSensor()
        #print(f"Starting light value: {startLightVal}")
        # Execute the movement of player left and right
        while (True):
            if not (compareLight(75, 100)):
                break
            sendCommand(g.ser, 'l' + delay + '\n', 0)
            if not (compareLight(75, 100)):
                break
            sendCommand(g.ser, 'r' + delay + '\n' , 0)
            if not (compareLight(75, 100)):
                break
        start = time.perf_counter()
        blackScreenLight = readSensor()
        #print(f"Black screen light level: {blackScreenLight}")
        while (True):
            if (compareLight(blackScreenLight, 200)):
                time.sleep(0.1)
                break
        time.sleep(0.75) # Sleep 1 second because of bright screen that appears for a short period of time
        # Start timer
        encounterLight = readSensor() # Light level while encounter occurs
        #print(f"Encounter light level: {encounterLight}")
        # Compare the light levels of the encounter screen and the "fight" button 
        while(compareLight(encounterLight, 20) == False):
            time.sleep(0.5)
        #print(f"Fight light level: {readSensor()}") # Light level when fight button appears
        # End timer when "fight" button appears on screen
        end = time.perf_counter()
        encounterDuration = end - start
        totalDuration += encounterDuration
        #print(f"Encounter duration: {encounterDuration} seconds")
        # Initialize encounter duration for rest of execution
        if (encounters == 0):
            input("Make sure the current encounter isn't shiny.\nPress enter to continue...")
            average = encounterDuration
        # If current encounter duration exceeds 1 seconds compared to the average of all encounters, declare that shiny has been found
        if(((encounterDuration) - average) > 1.0):
            while(True):
                option = input("Shiny has been found! Enter Y/N to confirm the shiny.\n").strip().lower()
                if (option in ['y', 'n']):
                    if option == 'y':
                        print("Congratulations on your shiny!")
                        shinyFound = True
                        break
                    else:
                        print("Shiny not found. Continuing execution...")
                        break
                else:
                    print("Invalid input, try again.")
        if(shinyFound == True):
            g.stop_threads = True
            break
        runAway()
        encounters += 1
        average = totalDuration / encounters
        print(f"Encounters: {encounters}, Encounter duration: {encounterDuration}, difference: {(encounterDuration - average)}, average: {average}")
        time.sleep(2) # Wait for screen to brighten back up from run away animation
        while(True):
            if compareLight(blackScreenLight, 50):
                break
            time.sleep(0.5)
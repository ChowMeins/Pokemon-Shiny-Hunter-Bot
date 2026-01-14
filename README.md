# Pokemon Shiny Hunter Bot

An automated shiny hunting program for Nintendo 3DS Pokemon games that uses computer vision and Arduino hardware to detect and hunt for shiny Pokemon encounters. The bot controls the 3DS hardware through servo motors and analyzes the game screen via webcam to identify shiny Pokemon.

## Supported Games

- **Pokemon Black 2 & White 2 (BW2)**: Starter Pokemon hunting
- **Pokemon HeartGold & SoulSilver (HGSS)**: Random encounter hunting

## Demo Showcase
**Results from hunting for Shiny Tepig in Pokemon Black 2**

<img  src='https://github.com/ChowMeins/Pokemon-Shiny-Hunter-Bot/blob/main/shinyFound.jpg' alt='Shiny Tepig'/>

**Results from random encountering in Pokemon HeartGold**

<img src='https://github.com/ChowMeins/Pokemon-Shiny-Hunter-Bot/blob/main/shinyFound2.png' alt='Shiny Bellsprout' />

## Hardware Requirements

### Required Components
- **Game Pro for 3DS**: Hardware controller interface
  - Purchase from [Nooby's Game Pro](https://www.noobysgamepro.com/)
- **Arduino Nano**: Microcontroller for button automation
- **USB Webcam**: For screen capture and analysis
- **Nintendo 3DS**: Compatible with supported Pokemon games

### Hardware Setup
The system uses servo motors controlled by Arduino to physically press the 3DS buttons, while a webcam monitors the screen for shiny Pokemon detection through computer vision algorithms.

## Software Requirements

### Dependencies
- **Python: (developed in 3.10, other versions not tested)**
- **OpenCV**: Computer vision library for image processing
- **Arduino IDE**: For uploading firmware to Arduino
- **Serial Communication Libraries**: For PC-Arduino communication

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/ChowMeins/Pokemon-Shiny-Hunter-Bot.git
   cd Pokemon-Shiny-Hunter-Bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install opencv-python
   pip install pyserial
   pip install numpy
   ```

3. **Arduino Setup**
   - Open `shinyHuntSetup.ino` in Arduino IDE
   - Connect Arduino Nano to your PC
   - Select the correct board and COM port
   - Upload the firmware to Arduino

## Setup Instructions

### Hardware Assembly
1. Connect the Game Pro hardware to your Nintendo 3DS
2. Connect servo motors to appropriate pins on Arduino Nano
3. Connect Arduino Nano to PC via USB
4. Position webcam to capture the 3DS screen clearly
5. Ensure stable lighting conditions for consistent image capture

### Software Configuration
1. **Arduino Configuration**
   - Upload `shinyHuntSetup.ino` to Arduino Nano
   - Verify correct COM port connection
   - Test servo motor functionality

2. **Camera Setup**
   - Position webcam for optimal 3DS screen capture
   - Calibrate camera settings for consistent image quality
   - Take initial reference photos for comparison

3. **Game Setup**
   - Load supported Pokemon game on 3DS
   - Navigate to appropriate hunting location
   - Ensure game is ready for automated inputs

## Usage

### Starting a Hunt
1. **Hardware Check**
   - Verify all connections are secure
   - Confirm Arduino is properly connected to correct COM port
   - Test webcam feed quality

2. **Launch Program**
   ```bash
   python main.py
   ```

3. **Initialize Hunt**
   - Program will take initial reference screenshot
   - Automated hunting sequence begins
   - Monitor console output for hunt progress

### Hunt Types

#### Starter Pokemon (BW2)
- Automates soft reset sequence for starter selection
- Detects shiny starter Pokemon through color analysis
- Stops automatically when shiny is found

#### Random Encounters (HGSS)
- Automates walking patterns to trigger encounters
- Analyzes encounter screens for shiny detection
- Continues until shiny Pokemon is encountered

## How It Works

### Detection Algorithm
1. **Image Capture**: Webcam continuously captures 3DS screen
2. **Image Processing**: OpenCV processes images for color analysis
3. **Shiny Detection**: Compares current Pokemon colors against reference images
4. **Decision Making**: Determines if Pokemon is shiny based on color differences
5. **Action Execution**: Either continues hunt or stops when shiny is found

### Control System
1. **Input Automation**: Arduino sends button inputs to 3DS via Game Pro
2. **Timing Control**: Precise timing ensures proper game state transitions
3. **Error Handling**: Monitors for unexpected game states or issues

## Results and Performance

### Pokemon BW2 Starter Hunt
- Successfully detects shiny starter Pokemon
- Automated soft reset functionality
- Consistent performance across multiple hunt sessions

### Pokemon HGSS Random Encounters
- Reliable random encounter triggering
- Accurate shiny detection in various lighting conditions
- Efficient hunt patterns to maximize encounters per hour

## Known Limitations

### Hardware Limitations
- **Servo Speed**: Servo motors operate slowly to preserve longevity, reducing hunt speed
- **Camera Quality**: Webcam quality can vary, affecting initial reference photo clarity
- **Lighting Sensitivity**: Detection accuracy depends on consistent lighting conditions

### Software Limitations
- **Image Quality Dependency**: Blurry reference photos may still yield results but with reduced accuracy
- **Game-Specific**: Currently limited to BW2 and HGSS games
- **Setup Sensitivity**: Requires precise camera positioning and calibration

## Troubleshooting

### Common Issues
- **Arduino Connection**: Verify correct COM port selection
- **Camera Focus**: Ensure webcam produces clear, focused images of 3DS screen
- **Servo Calibration**: Check servo motor alignment with 3DS buttons
- **Detection Accuracy**: Recalibrate reference images if detection seems inconsistent

### Performance Optimization
- Use consistent lighting conditions
- Ensure stable camera positioning
- Regular servo motor maintenance
- Periodic reference image updates

## Contributing

Contributions are welcome! Areas for improvement include:
- Additional game support
- Enhanced detection algorithms
- Hardware optimization
- Performance improvements
- Bug fixes and stability enhancements

### Development Guidelines
- Follow existing code structure and commenting standards
- Test thoroughly with actual hardware before submitting
- Document any new hardware requirements or setup steps
- Ensure compatibility with existing Arduino firmware

## Disclaimer

This project is for educational and personal use only. Users are responsible for complying with all applicable terms of service and local laws. The project does not encourage or endorse any violation of game terms of service.

## Technical Specifications

### Minimum System Requirements
- **Operating System**: Windows 10 or later
- **RAM**: 4GB minimum, 8GB recommended
- **USB Ports**: 2 available ports (Arduino + Webcam)

### Supported Hardware
- Arduino Nano (recommended)
- Compatible servo motors for 3DS button actuation
- USB webcam with manual focus capability
- Game Pro 3DS hardware interface

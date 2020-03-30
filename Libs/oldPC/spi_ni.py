from ctypes import *

# Create and init variables
firstDevice = create_string_buffer(256)  #create_string_buffer(b'\000' * 256)
findDeviceHandle = c_ulonglong(0)
numberFound = c_ulong(0)
deviceHandle = c_ulonglong(0)
spiHandle = c_ulonglong(0)
# Load dll
print("\nLoad the DLL")
dll = windll.LoadLibrary("Ni845x.dll")


# Function to output the status of the last command
def ni845xStatusToString(status):
    if status < 0:
        statusStr = create_string_buffer(1024)
        dll.ni845xStatusToString(status, 1024, statusStr)
        print("    " + str(statusStr.value))


# Function to close handle
def closeHandle():
    print("\nClose SPI communication")
    return dll.ni845xClose(deviceHandle.value)


# Function to check the error result
def checkError(statusCode):
    ni845xStatusToString(statusCode)
    if(statusCode<0):
        closeHandle()
        dll.ni845xSpiConfigurationClose(spiHandle.value)
        exit(1)


def spi_crc8Calc(array):
    nCRC = 0xFF
    for n in array:
        nCRC ^= n
        for bitnumber in range(0,8):
            if nCRC & 0x80:
                nCRC = (nCRC << 1) ^ 0x1D
            else:
                nCRC = nCRC << 1
    return (~nCRC) & 0xFF

def spi_init_ni_interface():
    print("\n\nINITIALIZATION")
    # Get devices
    print("   Searching for devices")
    checkError(dll.ni845xFindDevice(
        firstDevice,
        byref(findDeviceHandle),
        byref(numberFound)))

    # Open device
    print("   Start SPI communication")
    checkError(dll.ni845xOpen(
        firstDevice, 
        byref(deviceHandle)))

    # Set the I/O Voltage Level
    print("   Set the I/O voltage level")
    checkError(dll.ni845xSetIoVoltageLevel(
        deviceHandle.value,
        c_ubyte(33)))

    # Create configuration reference
    print("   Create configuration reference")
    checkError(dll.ni845xSpiConfigurationOpen(byref(spiHandle)))

    # Configure configuration properties
    print("   Configure configuration properties")
    checkError(dll.ni845xSpiConfigurationSetChipSelect(spiHandle.value, c_ulong(0)))
    checkError(dll.ni845xSpiConfigurationSetClockRate(spiHandle.value, c_uint16(1000)))
    checkError(dll.ni845xSpiConfigurationSetClockPolarity(spiHandle.value, c_int32(0)))
    checkError(dll.ni845xSpiConfigurationSetClockPhase(spiHandle.value, c_int32(1)))

    print("   Initialized successfully\n\n")

def spi_write_read(writeData):
    arrayData = c_uint8 * len(writeData)
    readData = arrayData(0,0,0,0,0,0)
    toSend = arrayData(*writeData)
    readSize = c_ulong(0)
    dll.ni845xSpiWriteRead (
        deviceHandle.value,
        spiHandle.value,
        len(writeData),
        byref(toSend),
        byref(readSize),
        byref(readData))
    # return the value converted into list of numbers
    return [x for x in readData]

# Close device
def spi_close_interface():
    checkError(closeHandle())
    checkError(dll.ni845xSpiConfigurationClose(spiHandle.value))

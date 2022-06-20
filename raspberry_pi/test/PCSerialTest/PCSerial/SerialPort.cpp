#include "SerialPort.h"
#include "message.h"

SerialPort::SerialPort(char *portName) {
    this->connected = false;

    this->handler = CreateFileA(static_cast<LPCSTR>(portName),
                                GENERIC_READ | GENERIC_WRITE,
                                0,
                                NULL,
                                OPEN_EXISTING,
                                FILE_ATTRIBUTE_NORMAL,
                                NULL);
    if (this->handler == INVALID_HANDLE_VALUE){
        if (GetLastError() == ERROR_FILE_NOT_FOUND){
            printf("ERROR: Handle was not attached. Reason: %s not available\n", portName);
        }
    else
        {
            printf("ERROR!!!");
        }
    }
    else {
        DCB dcbSerialParameters = {0};

        if (!GetCommState(this->handler, &dcbSerialParameters)) {
            printf("failed to get current serial parameters");
        }
        else {
            dcbSerialParameters.BaudRate = CBR_9600;
            dcbSerialParameters.ByteSize = 8;
            dcbSerialParameters.StopBits = ONESTOPBIT;
            dcbSerialParameters.Parity = NOPARITY;
            dcbSerialParameters.fDtrControl = DTR_CONTROL_ENABLE;

            if (!SetCommState(handler, &dcbSerialParameters))
            {
                printf("ALERT: could not set Serial port parameters\n");
            }
            else {
                this->connected = true;
                PurgeComm(this->handler, PURGE_RXCLEAR | PURGE_TXCLEAR);
                Sleep(WAIT_TIME);
            }
        }
    }
}

SerialPort::~SerialPort() {
    if (this->connected){
        this->connected = false;
        CloseHandle(this->handler);
    }
}

int SerialPort::readSerialPort(char *buffer, unsigned int buf_size) {
    DWORD bytesRead;
    unsigned int toRead = 0;

    ClearCommError(this->handler, &this->errors, &this->status);

    if (this->status.cbInQue > 0){
        if (this->status.cbInQue > buf_size){
            toRead = buf_size;
        }
        else toRead = this->status.cbInQue;
		if (ReadFile(this->handler, buffer, toRead, &bytesRead, NULL)) return bytesRead;
    }
    return 0;
}

bool SerialPort::writeSerialPort(char *buffer, unsigned int buf_size) {
    DWORD bytesSend;

    if (!WriteFile(this->handler, (void*) buffer, buf_size, &bytesSend, 0)){
        ClearCommError(this->handler, &this->errors, &this->status);
        return false;
    }
    else return true;
}

bool SerialPort::isConnected() {
	return this->connected;
}

uint8_t SerialPort::serial_message_received(void) {
	return serialMessageReceivedFlag;
}

unsigned char SerialPort::serial_receive_byte(void) {
	unsigned char uchr;
	int ret = readSerialPort((char*)&uchr, 1);
	if (ret) return uchr;
	return NULL;
}

void SerialPort::serial_send_byte(char chr) {
	writeSerialPort(&chr, 1);
}

void SerialPort::serial_send_float(float value) {
	uint32_t* val = (uint32_t*)&value;
	serial_send_byte((*val >> 0));
	serial_send_byte((*val >> 8));
	serial_send_byte((*val >> 16));
	serial_send_byte((*val >> 24));
}

void SerialPort::serial_send_vector(Vector3 data) {
	serial_send_float(data[0]);
	serial_send_float(data[1]);
	serial_send_float(data[2]);
}

void SerialPort::serial_send_electrical_info(float iReading, float vReading) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(ELECTRICAL_TYPE);
	serial_send_float(iReading);
	serial_send_float(vReading);
	serial_send_byte(SERIAL_ETX);
}

void SerialPort::serial_send_orientation_info(char key, Vector3 data) {
	if (key == MAGNETOMETER_TYPE || key == GYROSCOPE_TYPE) {
		serial_send_byte(SERIAL_STX);
		serial_send_byte(key);
		serial_send_vector(data);
		serial_send_byte(SERIAL_ETX);
	}
}

void SerialPort::serial_reply_to_command(char key) {
	serial_send_byte(SERIAL_STX);
	serial_send_byte(key);
	serial_send_byte('o');
	serial_send_byte('k');
	serial_send_byte(SERIAL_ETX);
}

int SerialPort::serial_check_for_message(void) {
	if (serialBuffer[currentPos] != SERIAL_ETX) {
		return 0;
	}
	//Just received an ETX
	int i;
	for (i = currentPos; i >= currentPos - MAX_MESSAGE_LENGTH; i--) {
		if (serialBuffer[i] == SERIAL_STX) {
			// there was an STX somewhere before the ETX
			break;
		}
	}

	return 0;
}

int serial_convert_message_type_to_length(unsigned char type) {
	switch (type) {
	case ORIENTATION_TYPE:
		return sizeof(float) * 2;
	case POWER_CYCLE_TYPE:
		return sizeof(uint8_t);
	case SEARCH_MODE_TYPE:
		return sizeof(uint8_t);
	case CALIBRATE_TYPE:
		return sizeof(uint8_t);
	case DEBUG_LED_TYPE:
		return sizeof(uint8_t);
	default:
		return -1;
	}
}

int SerialPort::serial_check_message_received(void) {
	return serialMessageReceivedFlag;
}

SerialMessage SerialPort::serial_get_last_message(void) {
	serialMessageReceivedFlag = 0;
	serial_reply_to_command(lastMessage.messageType);
	return lastMessage;
}

void SerialPort::serial_construct_message(void) {
	unsigned char type = serialBuffer[1];
	lastMessage.messageType = type;

	switch (type) {
	case ORIENTATION_TYPE:
		//Orientation command
		//this should be followed by 2 floats;
		for (int i = 0; i < 2; i++) {
			//possibly swap around if endianness is wrong???
			unsigned char bytes[] = { serialBuffer[4 * i + 2],
				serialBuffer[4 * i + 3],
				serialBuffer[4 * i + 4],
				serialBuffer[4 * i + 5] };
			memcpy(&lastMessage.data.angles[i], bytes, sizeof(float));
		}
		break;

	case POWER_CYCLE_TYPE:
		lastMessage.data.value = serialBuffer[2];
		break;
	case SEARCH_MODE_TYPE:
		lastMessage.data.value = serialBuffer[2];
		break;
	case CALIBRATE_TYPE:
		lastMessage.data.value = serialBuffer[2];
		break;
	case DEBUG_LED_TYPE:
		lastMessage.data.value = serialBuffer[2];
		break;
	default:
		break;
	}

	serialMessageReceivedFlag = 1; //possibly raise a software interrupt to handle this??
}

void SerialPort::update_buffer(void) {
	//Put the character into the buffer
	serialBuffer[currentPos] = serial_receive_byte();
#if ECHO_SERIAL
	serial_send_byte(serialBuffer[currentPos]);
#endif

	if (waitingForStx && serialBuffer[currentPos] == SERIAL_STX) {
		waitingForStx = 0; //received the stx
		currentPos++;
	}
	else if (currentPos == 1) {
		//this is the first character which signifies type of message
		messageLength = serial_convert_message_type_to_length(serialBuffer[currentPos]);
		if (messageLength == -1) {
			//this message type was not valid
			//reset everything
			currentPos = 0;
			waitingForStx = 1;
		}
		else {
			currentPos++;
		}
	}
	else if (!waitingForStx) {
		//we are in the midst of receiving a message 
		if (currentPos == messageLength + 2) { //+2 because STX and messageType
											   //this should be the end of the message
			if (serialBuffer[currentPos] == SERIAL_ETX) {
				//the ETX came through as expected
				serial_construct_message();

			}
			//got enough data but this should have been an ETX, reset everything
			currentPos = 0;
			waitingForStx = 1;
		}
		else {
			currentPos++;
		}
	}
	else {
		//we're waiting for an stx but haven't received one.
		//Probably missed the start of the message
		//just continue and wait for the next stx
		;
	}
}
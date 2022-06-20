/** 
 *  Code for Raspberry Pi UART testing with FTDI in Windows.
 *	
 *  Date: 02/05/2018
 */

#include "SerialPort.h"
#include <iostream>

using namespace std;

/* Get input from the console */
size_t getline(char **lineptr, size_t *n, FILE *stream) {
	char *bufptr = NULL;
	char *p = bufptr;
	size_t size;
	int c;

	if (lineptr == NULL) {
		return -1;
	}
	if (stream == NULL) {
		return -1;
	}
	if (n == NULL) {
		return -1;
	}
	bufptr = *lineptr;
	size = *n;

	c = fgetc(stream);
	if (c == EOF) {
		return -1;
	}
	if (bufptr == NULL) {
		bufptr = (char*)malloc(128);
		if (bufptr == NULL) {
			return -1;
		}
		size = 128;
	}
	p = bufptr;
	while (c != EOF) {
		if ((p - bufptr) > (size - 1)) {
			size = size + 128;
			bufptr = (char*)realloc(bufptr, size);
			if (bufptr == NULL) {
				return -1;
			}
		}
		*p++ = c;
		if (c == '\n') {
			break;
		}
		c = fgetc(stream);
	}

	*p++ = '\0';
	*lineptr = bufptr;
	*n = size;

	return p - bufptr - 1;
}

int main(int argc, char* argv[]) {
	char* port = "\\\\.\\COM6";
	SerialPort *piLink = new SerialPort(port);

	Vector3 magnetometerData = { 4.56, 5.7, 6.56 };
	Vector3 gyroscopeData = { 444.0, 777.04, 667.6 };
	float iReading = 0.7;
	float vReading = 4.5;
	SerialMessage lastMessage;

	while (piLink->isConnected()) {
		/* Try reading messages */
		piLink->update_buffer();
		if (piLink->serial_message_received()) {
			lastMessage = piLink->serial_get_last_message();
			char* key = &lastMessage.messageType;
			printf(key);
			if (key[0] == ORIENTATION_TYPE) {
				printf("%f,%f\n", 
					lastMessage.data.angles[0], 
					lastMessage.data.angles[1]);
			} else {
				printf("%d\n", lastMessage.data.value);
			}
		}

		/* Try sending messages */
		/*
		piLink->serial_send_electrical_info(iReading, vReading);
		piLink->serial_send_orientation_info(MAGNETOMETER_TYPE, magnetometerData);
		piLink->serial_send_orientation_info(GYROSCOPE_TYPE, gyroscopeData);
		*/
		Sleep(100); 
	}
	cout << "Failed to open the port!" << endl;
	system("pause");
}
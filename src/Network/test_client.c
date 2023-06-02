#include <zephyr/kernel.h> 
#include <zephyr/drivers/gpio.h> 
#include <zephyr/sys/printk.h> 
#include <zephyr/net/openthread.h> 
#include <openthread/thread.h> 
#include <openthread/udp.h> 
#include <openthread/coap.h>
#include <stdio.h>

#define SLEEP_TIME_MS 20 

char moduleID[10] = "683279187";
int16_t w = 321;
int16_t x = 123;
int16_t y = 231;
int16_t z = 312;

static void send_quaternion_run(void){
	otError error = OT_ERROR_NONE;

	char buffer[50];
	sprintf(buffer, "%s, %6d, %6d, %6d, %6d\n", moduleID, w, x, y, z);

	otInstance *myInstance; 
	myInstance = openthread_get_default_instance(); 
	otUdpSocket mySocket;

	otMessageInfo messageInfo; 
	memset(&messageInfo, 0, sizeof(messageInfo));

	//otIp6AddressFromString("ff03::1", &messageInfo.mPeerAddr);

	const otMeshLocalPrefix *ml_prefix = otThreadGetMeshLocalPrefix(myInstance);
	uint8_t serverInterfaceID[8]= {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01};

	memcpy(&messageInfo.mPeerAddr.mFields.m8[0], ml_prefix, 8);
	memcpy(&messageInfo.mPeerAddr.mFields.m8[8], serverInterfaceID, 8);

	messageInfo.mPeerPort = 1234;

	do{ 	
		error = otUdpOpen(myInstance, &mySocket, NULL, NULL);
		if (error != OT_ERROR_NONE){ break; }
		
		otMessage *test_Message = otUdpNewMessage(myInstance, NULL);
		error = otMessageAppend(test_Message, buffer, (uint16_t)strlen(buffer)); 
		if (error != OT_ERROR_NONE){ break; } 
		
		error = otUdpSend(myInstance, &mySocket, test_Message, &messageInfo); 
		if (error != OT_ERROR_NONE){ break; }
		error = otUdpClose(myInstance, &mySocket); 

	} while(false); 
		if (error == OT_ERROR_NONE){ 
			printk("Send.\n"); 
		} else{ 
			printk("udpSend error: %d\n", error); 
	} 
}

void main(void){ 
	while (1) { 
		send_quaternion_run();
		k_msleep(SLEEP_TIME_MS); 
	} 
}

#include <zephyr/kernel.h> 
#include <zephyr/drivers/gpio.h> 
#include <zephyr/sys/printk.h> 
#include <zephyr/net/openthread.h> 
#include <openthread/thread.h> 
#include <openthread/udp.h> 

#define SLEEP_TIME_MS 1000 

void udpReceiveCb(void *aContext, otMessage *aMessage, const otMessageInfo *aMessageInfo){ 
	uint16_t payloadLength = otMessageGetLength(aMessage) - otMessageGetOffset(aMessage);
	char buf[payloadLength+1];
	otMessageRead(aMessage, otMessageGetOffset(aMessage), buf, payloadLength);
	buf[payloadLength]='\0'; printk("Received: %s\n",buf); 
}

void addIPv6Address(void){ 
	otInstance *myInstance = openthread_get_default_instance();
	otNetifAddress aAddress;
	const otMeshLocalPrefix *ml_prefix = otThreadGetMeshLocalPrefix(myInstance);
	uint8_t interfaceID[8]= {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01}; 
	
	memcpy(&aAddress.mAddress.mFields.m8[0], ml_prefix, 8); 
	memcpy(&aAddress.mAddress.mFields.m8[8], interfaceID, 8); 
	
	otError error = otIp6AddUnicastAddress(myInstance, &aAddress); 
	
	if (error != OT_ERROR_NONE) 
		printk("addIPAdress Error: %d\n", error); 
}

static void udp_init(void){ 
	otError error = OT_ERROR_NONE; 

	otInstance *myInstance; 
	myInstance = openthread_get_default_instance(); 
	otUdpSocket mySocket; 

	otSockAddr mySockAddr;
	memset(&mySockAddr, 0, sizeof(mySockAddr));

	//const otMeshLocalPrefix *ml_prefix = otThreadGetMeshLocalPrefix(myInstance);
	//uint8_t interfaceID[8]= {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01}; 
	
	//memcpy(&mySockAddr.mAddress.mFields.m8[0], ml_prefix, 8); 
	//memcpy(&mySockAddr.mAddress.mFields.m8[8], interfaceID, 8);

	mySockAddr.mPort = 1234; 
	
	do{ 
		error = otUdpOpen(myInstance, &mySocket, udpReceiveCb, NULL); 
		if (error != OT_ERROR_NONE){ break; } 
		
		error = otUdpBind(myInstance, &mySocket, &mySockAddr, OT_NETIF_THREAD); 
		
		}while (false); 
		
		if (error != OT_ERROR_NONE){ 
			printk("init_udp error: %d\n", error);
		} 
}

void main(void){ 
	addIPv6Address();
	udp_init();
	while (1) {
		k_msleep(SLEEP_TIME_MS);
	}	 
}

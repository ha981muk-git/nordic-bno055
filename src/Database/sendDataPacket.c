#include <zephyr/kernel.h> 
#include <zephyr/sys/printk.h> 

#define SLEEP_TIME_MS 50 

// Small Program to send Datapackets for tests
void main(void){ 
	int16_t x = 0;
	int16_t y = 0;
	int16_t z = 0;
	while (1) { 
		printk("%6d,%6d,%6d\n", x, y, z); 
		k_msleep(SLEEP_TIME_MS);
		x++;
		y+=2;
		z+=3; 
	} 
}

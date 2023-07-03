#include <zephyr/kernel.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/smf.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/net/openthread.h> 
#include <openthread/thread.h> 
#include <openthread/udp.h> 
#include <openthread/coap.h>
#include <stdio.h>

#define SLEEP_TIME_MS 1000

#define LED0_NODE DT_NODELABEL(led0)
#define LED1_NODE DT_NODELABEL(led1)
#define LED2_NODE DT_NODELABEL(led2)
#define LED3_NODE DT_NODELABEL(led3)
static const struct gpio_dt_spec led0_spec = GPIO_DT_SPEC_GET(LED0_NODE, gpios);
static const struct gpio_dt_spec led1_spec = GPIO_DT_SPEC_GET(LED1_NODE, gpios);
static const struct gpio_dt_spec led2_spec = GPIO_DT_SPEC_GET(LED2_NODE, gpios);
static const struct gpio_dt_spec led3_spec = GPIO_DT_SPEC_GET(LED3_NODE, gpios);

#define I2C_NODE DT_NODELABEL(i2c0)

/********************************************************/
/*I2C ADDRESS*/
/********************************************************/
#define BNO055_ADDRESS_A (0x28)

/***************************************************/
/*REGISTER ADDRESS*/
/***************************************************/
/* Page id register definition*/

#define BNO055_PAGE_ID_ADDR (0X07)

/* PAGE0 REGISTER DEFINITION START*/
#define BNO055_CHIP_ID_ADDR (0x00)

/* Accel data register*/
#define BNO055_ACCEL_DATA_X_LSB_ADDR (0X08)
#define BNO055_ACCEL_DATA_X_MSB_ADDR (0X09)
#define BNO055_ACCEL_DATA_Y_LSB_ADDR (0X0A)
#define BNO055_ACCEL_DATA_Y_MSB_ADDR (0X0B)
#define BNO055_ACCEL_DATA_Z_LSB_ADDR (0X0C)
#define BNO055_ACCEL_DATA_Z_MSB_ADDR (0X0D)

/*Gyro data registers*/
#define BNO055_GYRO_DATA_X_LSB_ADDR (0X14)
#define BNO055_GYRO_DATA_X_MSB_ADDR (0X15)
#define BNO055_GYRO_DATA_Y_LSB_ADDR (0X16)
#define BNO055_GYRO_DATA_Y_MSB_ADDR (0X17)
#define BNO055_GYRO_DATA_Z_LSB_ADDR (0X18)
#define BNO055_GYRO_DATA_Z_MSB_ADDR (0X19)

/*Euler data registers*/
#define BNO055_EULER_H_LSB_ADDR (0X1A)
#define BNO055_EULER_H_MSB_ADDR (0X1B)

#define BNO055_EULER_R_LSB_ADDR (0X1C)
#define BNO055_EULER_R_MSB_ADDR (0X1D)

#define BNO055_EULER_P_LSB_ADDR (0X1E)
#define BNO055_EULER_P_MSB_ADDR (0X1F)


/* Status registers*/
#define BNO055_CALIB_STAT_ADDR (0X35)

/* Mode registers*/
#define BNO055_OPR_MODE_ADDR (0X3D)

#define BNO055_SYS_TRIGGER_ADDR (0X3F)

// Operation Modes
#define OPERATION_MODE_CONFIG (0x00)
#define OPERATION_MODE_IMU (0x08)

static const struct device *i2c_dev = DEVICE_DT_GET(I2C_NODE);

static uint8_t write_i2c_buffer[2];
static uint8_t read_i2c_buffer[8];

static int32_t sleep_msec = 0;

struct
{
	uint8_t device_id;
	uint8_t accel_cali;
	uint8_t gyro_cali;
	uint8_t system_cali;
	int16_t accel_x;
	int16_t accel_y;
	int16_t accel_z;
	int16_t gyro_x;
	int16_t gyro_y;
	int16_t gyro_z;
	bool isCalibrated;

} bno055;
char moduleID[10] = "683519779";
static const struct smf_state states[];

enum state
{
	CHECKID,
	SETOPMODETOCONFIG,
	SETPAGEID,
	SETEXTERNALCRYSTAL,
	SETOPMODETOIMU,
	READDATA,
	READCALIBRATION,
	SENDDATA
};

struct s_object
{
	struct smf_ctx ctx;
} s_obj;

static void read_device_id()
{
	write_i2c_buffer[0] = BNO055_CHIP_ID_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("READ_DEVICE_ID_ failed: %d\n", err);
	}
	else
	{
		bno055.device_id = read_i2c_buffer[0];
		printk("CHIP ID: 0x%02X \n", bno055.device_id);
		sleep_msec = 1000;
		smf_set_state(SMF_CTX(&s_obj), &states[SETOPMODETOCONFIG]);
	}
}

static void set_op_mode_to_config()
{
	write_i2c_buffer[0] = BNO055_OPR_MODE_ADDR;
	write_i2c_buffer[1] = OPERATION_MODE_CONFIG;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 2, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("SET_OP_MODE_TO_CONFIG failed: %d\n", err);
	}
	else
	{
		printk("Operation Mode is set to: 0x%02X \n", read_i2c_buffer[0]);
		sleep_msec = 20;
		smf_set_state(SMF_CTX(&s_obj), &states[SETPAGEID]);
	}
}

static void set_page_id()
{
	write_i2c_buffer[0] = BNO055_PAGE_ID_ADDR;
	write_i2c_buffer[1] = 0x00;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 2, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("SET_PAGE_ID failed: %d\n", err);
	}
	else
	{
		printk("PAGE ID: 0x%02X \n", read_i2c_buffer[0]);
		sleep_msec = 0;
		smf_set_state(SMF_CTX(&s_obj), &states[SETEXTERNALCRYSTAL]);
	}
}

static void set_external_crystal()
{
	write_i2c_buffer[0] = BNO055_SYS_TRIGGER_ADDR;
	write_i2c_buffer[1] = 0x80;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 2, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("SET_EXTERNAL_CRYSTAL failed: %d\n", err);
	}
	else
	{
		printk("External crystal is set to: 0x%02X \n", read_i2c_buffer[0]);
		sleep_msec = 600;
		smf_set_state(SMF_CTX(&s_obj), &states[SETOPMODETOIMU]);
	}
}

static void set_op_mode_to_imu()
{
	write_i2c_buffer[0] = BNO055_OPR_MODE_ADDR;
	write_i2c_buffer[1] = OPERATION_MODE_IMU;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 2, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("SET_OP_MODE_TO_CONFIG_IMU failed: %d\n", err);
	}
	else
	{
		printk("Operation Mode is set to: 0x%02X \n", read_i2c_buffer[0]);
		sleep_msec = 80;
		smf_set_state(SMF_CTX(&s_obj), &states[READDATA]);
	}
}

static void read_gryoscope_data()
{
	write_i2c_buffer[0] = BNO055_GYRO_DATA_X_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_i2c_buffer, 6);
	if (err < 0)
	{
		printk("READ_GRYOSCOPE_DATA failed: %d\n", err);
	}
	else
	{
		bno055.gyro_x = (((uint16_t)read_i2c_buffer[1]) << 8) | ((uint16_t)read_i2c_buffer[0]);
		bno055.gyro_y = (((uint16_t)read_i2c_buffer[3]) << 8) | ((uint16_t)read_i2c_buffer[2]);
		bno055.gyro_z = (((uint16_t)read_i2c_buffer[5]) << 8) | ((uint16_t)read_i2c_buffer[4]);
		printk("Gyro Data: X:%d Y:%d Z:%d\n", bno055.gyro_x, bno055.gyro_y, bno055.gyro_z);
	}
}

static void read_acceleration_data()
{
	write_i2c_buffer[0] = BNO055_ACCEL_DATA_X_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_i2c_buffer, 6);
	if (err < 0)
	{
		printk("READ_ACCELERATION_DATA failed: %d\n", err);
	}
	else
	{
		bno055.accel_x = (((uint16_t)read_i2c_buffer[1]) << 8) | ((uint16_t)read_i2c_buffer[0]);
		bno055.accel_y = (((uint16_t)read_i2c_buffer[3]) << 8) | ((uint16_t)read_i2c_buffer[2]);
		bno055.accel_z = (((uint16_t)read_i2c_buffer[5]) << 8) | ((uint16_t)read_i2c_buffer[4]);
		printk("Accel Data: X:%d Y:%d Z:%d\n", bno055.accel_x, bno055.accel_y, bno055.accel_z);
	}
}

static void read_data()
{
	read_acceleration_data();
	read_gryoscope_data();
	if (bno055.isCalibrated)
	{
		sleep_msec = 500;
		smf_set_state(SMF_CTX(&s_obj), &states[SENDDATA]);
	}
	else
	{
		sleep_msec = 500;
		printk("Calibrating....\n");
		smf_set_state(SMF_CTX(&s_obj), &states[READCALIBRATION]);
	}
}

static void read_calibration_data()
{
	write_i2c_buffer[0] = BNO055_CALIB_STAT_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_i2c_buffer, 1);
	if (err < 0)
	{
		printk("READ_CALIB_STAT failed: %d\n", err);
	}
	else
	{
		bno055.accel_cali = (read_i2c_buffer[0] >> 2) & 0x03;
		bno055.gyro_cali = (read_i2c_buffer[0] >> 4) & 0x03;
		bno055.system_cali = (read_i2c_buffer[0] >> 6) & 0x03;
		if (bno055.accel_cali == 3)
		{
			gpio_pin_set_dt(&led0_spec, 1);
		}
		if (bno055.gyro_cali == 3)
		{
			gpio_pin_set_dt(&led1_spec, 1);
		}
		if (bno055.system_cali == 0)
		{
			gpio_pin_set_dt(&led2_spec, 1);
		}
		if (read_i2c_buffer[0] >= 0x3C)
		{
			bno055.isCalibrated = true;
		}
		else
		{
			bno055.isCalibrated = false;
		}
		smf_set_state(SMF_CTX(&s_obj), &states[READDATA]);
	}
}
static void send_data(void){
    otError error = OT_ERROR_NONE;

	char buffer[80];
	sprintf(buffer, "%s, %6d, %6d, %6d, %6d, %6d, %6d\n", moduleID, bno055.accel_x, bno055.accel_y, bno055.accel_z, bno055.gyro_x, bno055.gyro_y, bno055.gyro_z);

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
	smf_set_state(SMF_CTX(&s_obj), &states[READDATA]);
}

static const struct smf_state states[] = {
	[CHECKID] = SMF_CREATE_STATE(NULL, read_device_id, NULL),
	[SETOPMODETOCONFIG] = SMF_CREATE_STATE(NULL, set_op_mode_to_config, NULL),
	[SETPAGEID] = SMF_CREATE_STATE(NULL, set_page_id, NULL),
	[SETEXTERNALCRYSTAL] = SMF_CREATE_STATE(NULL, set_external_crystal, NULL),
	[SETOPMODETOIMU] = SMF_CREATE_STATE(NULL, set_op_mode_to_imu, NULL),
	[READDATA] = SMF_CREATE_STATE(NULL, read_data, NULL),
	[READCALIBRATION] = SMF_CREATE_STATE(NULL, read_calibration_data, NULL),
	[SENDDATA] = SMF_CREATE_STATE(NULL, send_data, NULL)};

void main(void)
{
	if (!device_is_ready(i2c_dev))
	{
		printk("i2c_dev not ready\n");
		return;
	}
	bno055.isCalibrated = false;

	gpio_pin_configure_dt(&led0_spec, GPIO_OUTPUT);
	gpio_pin_configure_dt(&led1_spec, GPIO_OUTPUT);
	gpio_pin_configure_dt(&led2_spec, GPIO_OUTPUT);
	gpio_pin_configure_dt(&led3_spec, GPIO_OUTPUT);
	gpio_pin_set_dt(&led0_spec, 0);
	gpio_pin_set_dt(&led1_spec, 0);
	gpio_pin_set_dt(&led2_spec, 0);
	gpio_pin_set_dt(&led3_spec, 0);

	int32_t ret;

	smf_set_initial(SMF_CTX(&s_obj), &states[CHECKID]);

	while (true)
	{
		ret = smf_run_state(SMF_CTX(&s_obj));
		if (ret)
		{
			printk("Error: %d\n", ret);
			smf_set_initial(SMF_CTX(&s_obj), &states[CHECKID]);
			sleep_msec = 5000;
		}
		k_msleep(sleep_msec);
	}
}

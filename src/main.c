#include <zephyr/kernel.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/smf.h>
#include <zephyr/drivers/gpio.h>

#define SLEEP_TIME_MS 1000
#define I2C_NODE DT_NODELABEL(i2c0)
#define READ_SENSOR_INTERVALL 50
#define ERROR_SLEEP 5000

/********************************************************/
/**\name    I2C ADDRESS DEFINITION FOR BNO055           */
/********************************************************/
#define BNO055_ADDRESS_A (0x28)
#define BNO055_ADDRESS_B (0x29)

/***************************************************/
/**\name    REGISTER ADDRESS DEFINITION  */
/***************************************************/
/* Page id register definition*/

#define BNO055_PAGE_ID_ADDR (0X07)

/* PAGE0 REGISTER DEFINITION START*/
#define BNO055_CHIP_ID_ADDR (0x00)
#define BNO055_ACCEL_REV_ID_ADDR (0x01)
#define BNO055_MAG_REV_ID_ADDR (0x02)
#define BNO055_GYRO_REV_ID_ADDR (0x03)
#define BNO055_SW_REV_ID_LSB_ADDR (0x04)
#define BNO055_SW_REV_ID_MSB_ADDR (0x05)
#define BNO055_BL_REV_ID_ADDR (0X06)

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

/*Quaternion data registers*/
#define BNO055_QUATERNION_DATA_W_LSB_ADDR (0X20)
#define BNO055_QUATERNION_DATA_W_MSB_ADDR (0X21)
#define BNO055_QUATERNION_DATA_X_LSB_ADDR (0X22)
#define BNO055_QUATERNION_DATA_X_MSB_ADDR (0X23)
#define BNO055_QUATERNION_DATA_Y_LSB_ADDR (0X24)
#define BNO055_QUATERNION_DATA_Y_MSB_ADDR (0X25)
#define BNO055_QUATERNION_DATA_Z_LSB_ADDR (0X26)
#define BNO055_QUATERNION_DATA_Z_MSB_ADDR (0X27)

/* Linear acceleration data registers*/
#define BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR (0X28)
#define BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR (0X29)
#define BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR (0X2A)
#define BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR (0X2B)
#define BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR (0X2C)
#define BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR (0X2D)

/* Status registers*/
#define BNO055_CALIB_STAT_ADDR (0X35)
#define BNO055_SELFTEST_RESULT_ADDR (0X36)
#define BNO055_INTR_STAT_ADDR (0X37)
#define BNO055_SYS_CLK_STAT_ADDR (0X38)
#define BNO055_SYS_STAT_ADDR (0X39)
#define BNO055_SYS_ERR_ADDR (0X3A)

/* Unit selection register*/
#define BNO055_UNIT_SEL_ADDR (0X3B)
#define BNO055_DATA_SELECT_ADDR (0X3C)

/* Mode registers*/
#define BNO055_OPR_MODE_ADDR (0X3D)
#define BNO055_PWR_MODE_ADDR (0X3E)

#define BNO055_SYS_TRIGGER_ADDR (0X3F)
#define BNO055_TEMP_SOURCE_ADDR (0X40)
/* PAGE0 REGISTERS DEFINITION END*/

/* PAGE1 REGISTERS DEFINITION START*/
/* Configuration registers*/
#define BNO055_ACCEL_CONFIG_ADDR (0X08)
#define BNO055_MAG_CONFIG_ADDR (0X09)
#define BNO055_GYRO_CONFIG_ADDR (0X0A)
#define BNO055_GYRO_MODE_CONFIG_ADDR (0X0B)
#define BNO055_ACCEL_SLEEP_CONFIG_ADDR (0X0C)
#define BNO055_GYRO_SLEEP_CONFIG_ADDR (0X0D)
#define BNO055_MAG_SLEEP_CONFIG_ADDR (0x0E)

/***************************************************/
/**\name    Operation Modes  */
/***************************************************/
// Operation Modes
#define OPERATION_MODE_CONFIG (0x00)
#define OPERATION_MODE_ACCGYRO (0x05)

#define OPERATION_MODE_IMU (0x08)
#define OPERATION_MODE_NDOF (0x0C)

static const struct device *i2c_dev = DEVICE_DT_GET(I2C_NODE);

static uint8_t write_i2c_buffer[2];
static uint8_t read_ic2_buffer[8];

struct
{
	uint8_t device_id;
	uint8_t mag_cali;
	uint8_t accel_cali;
	uint8_t gyro_cali;
	uint8_t system_cali;
	int16_t quat_w;
	int16_t quat_x;
	int16_t quat_y;
	int16_t quat_z;
	int16_t accel_x;
	int16_t accel_y;
	int16_t accel_z;
	int16_t gyro_x;
	int16_t gyro_y;
	int16_t gyro_z;
	int16_t euler_head;
	int16_t euler_roll;
	int16_t euler_pitch;
	bool isCalibrated;

} bno055;

static void read_deviceID()
{
	write_i2c_buffer[0] = BNO055_CHIP_ID_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 1);
	if (err < 0)
	{
		printk("READ_DEVICE_ID_ failed: %d\n", err);
	}
	else
	{
		bno055.device_id = read_ic2_buffer[0];
		printk("CHIP ID: 0x%02X \n", bno055.device_id);
	}
}

static void read_op_mode()
{
	write_i2c_buffer[0] = BNO055_OPR_MODE_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 1);
	if (err < 0)
	{
		printk("READ_DEVICE_ID_ failed: %d\n", err);
	}
	else
	{
		printk("Operation Mode: 0x%02X \n", read_ic2_buffer[0]);
	}
}

// to-do: User soll entscheiden können welchen Modus er haben will.
static void set_op_mode()
{
	write_i2c_buffer[0] = BNO055_OPR_MODE_ADDR;
	write_i2c_buffer[1] = OPERATION_MODE_NDOF;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 2, read_ic2_buffer, 1);
	if (err < 0)
	{
		printk("READ_DEVICE_ID_ failed: %d\n", err);
	}
	else
	{
		printk("Operation Mode is set to: 0x%02X \n", read_ic2_buffer[0]);
	}
}

static void read_gryoscope_data()
{
	write_i2c_buffer[0] = BNO055_GYRO_DATA_X_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 6);
	if (err < 0)
	{
		printk("READ_QUATERNION_DATA failed: %d\n", err);
	}
	else
	{
		bno055.gyro_x = (((uint16_t)read_ic2_buffer[1]) << 8) | ((uint16_t)read_ic2_buffer[0]);
		bno055.gyro_y = (((uint16_t)read_ic2_buffer[3]) << 8) | ((uint16_t)read_ic2_buffer[2]);
		bno055.gyro_z = (((uint16_t)read_ic2_buffer[5]) << 8) | ((uint16_t)read_ic2_buffer[4]);
		printk("Gyro Data: X:%d Y:%d Z:%d\n", bno055.gyro_x, bno055.gyro_y, bno055.gyro_z);
	}
}

static void read_euler_data()
{
	write_i2c_buffer[0] = BNO055_EULER_H_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 6);
	if (err < 0)
	{
		printk("READ_QUATERNION_DATA failed: %d\n", err);
	}
	else
	{
		bno055.euler_head = (((uint16_t)read_ic2_buffer[1]) << 8) | ((uint16_t)read_ic2_buffer[0]);
		bno055.euler_roll = (((uint16_t)read_ic2_buffer[3]) << 8) | ((uint16_t)read_ic2_buffer[2]);
		bno055.euler_pitch = (((uint16_t)read_ic2_buffer[5]) << 8) | ((uint16_t)read_ic2_buffer[4]);
		printk("Euler Data: X:%d Y:%d Z:%d\n", bno055.euler_head, bno055.euler_pitch, bno055.euler_roll);
	}
}

static void read_acceleration_data()
{
	write_i2c_buffer[0] = BNO055_ACCEL_DATA_X_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 6);
	if (err < 0)
	{
		printk("READ_QUATERNION_DATA failed: %d\n", err);
	}
	else
	{
		bno055.accel_x = (((uint16_t)read_ic2_buffer[1]) << 8) | ((uint16_t)read_ic2_buffer[0]);
		bno055.accel_y = (((uint16_t)read_ic2_buffer[3]) << 8) | ((uint16_t)read_ic2_buffer[2]);
		bno055.accel_z = (((uint16_t)read_ic2_buffer[5]) << 8) | ((uint16_t)read_ic2_buffer[4]);
		printk("Accel Data: X:%d Y:%d Z:%d\n", bno055.accel_x, bno055.accel_y, bno055.accel_z);
	}
}

static void read_quaternion_data()
{
	write_i2c_buffer[0] = BNO055_QUATERNION_DATA_W_LSB_ADDR;
	int err = i2c_write_read(i2c_dev, BNO055_ADDRESS_A, write_i2c_buffer, 1, read_ic2_buffer, 8);
	if (err < 0)
	{
		printk("READ_QUATERNION_DATA failed: %d\n", err);
	}
	else
	{
		bno055.quat_w = (((uint16_t)read_ic2_buffer[1]) << 8) | ((uint16_t)read_ic2_buffer[0]);
		bno055.quat_x = (((uint16_t)read_ic2_buffer[3]) << 8) | ((uint16_t)read_ic2_buffer[2]);
		bno055.quat_y = (((uint16_t)read_ic2_buffer[5]) << 8) | ((uint16_t)read_ic2_buffer[4]);
		bno055.quat_z = (((uint16_t)read_ic2_buffer[7]) << 8) | ((uint16_t)read_ic2_buffer[6]);
		printk("Quat Data: W:%d X:%d Y:%d Z:%d\n", bno055.quat_w, bno055.quat_x, bno055.quat_y, bno055.quat_z);
	}
}

// to-do User soll die erfassung der Daten stoppen können.
void main(void)
{
	if (!device_is_ready(i2c_dev))
	{
		printk("i2c_dev not ready\n");
		return;
	}
	bno055.isCalibrated = false;
	read_op_mode();
	while (true)
	{
		read_gryoscope_data();
		read_acceleration_data();
		read_quaternion_data();
		read_euler_data();
		k_msleep(SLEEP_TIME_MS);
	}
}
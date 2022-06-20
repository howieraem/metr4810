/*
 * img_tele_power.h
 *
 * Created: 29/04/2018 2:45:35 PM
 *  
 */ 


#ifndef IMG_TELE_POWER_H_
#define IMG_TELE_POWER_H_

#define IMG_PWR_CTL_PIN PINC0
#define IMG_SHT_CTL_PIN PINC1
#define IMG_CAM_CTL_PIN PINC2

#define IMG_CTL_PORT PORTC
#define IMG_CTL_DDR DDRC

/*
 * Turn the power to the telecomunication and imaging off and on
 */
#define img_tele_power_off() IMG_CTL_PORT |= (1 << IMG_PWR_CTL_PIN)
#define img_tele_power_on() IMG_CTL_PORT &= ~(1 << IMG_PWR_CTL_PIN)

/*
 * Toggles a gpio pin to issue a shutdown request
 */
#define img_tele_shutdown_off() IMG_CTL_PORT &= ~(1 << IMG_SHT_CTL_PIN)
#define img_tele_shutdown_on() IMG_CTL_PORT |= (1 << IMG_SHT_CTL_PIN)
 
/*
 * Turn the camera on/off
 */
#define img_tele_camera_off() IMG_CTL_PORT &= ~(1 << IMG_CAM_CTL_PIN)
#define img_tele_camera_on() IMG_CTL_PORT |= (1 << IMG_CAM_CTL_PIN)

/*
 * Initialise all the hardware for turning things off and on
 */
void img_tele_power_init(void);

/*
 * Power cycle the imaging and telemetry
 */
void img_tele_power_cycle(void);

/*
 * Power cycle the shutdown for imaging and telemetry
 */
void img_tele_shutdown_cycle(void);

/*
 * Power cycle the camera
 */
void img_tele_camera_cycle(void);



#endif /* IMG_TELE_POWER_H_ */
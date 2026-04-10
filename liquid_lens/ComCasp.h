#ifndef __COMCASP_OL_H__
#define __COMCASP_OL_H__

/** \defgroup ComFunc Communication management functions
  * Etablish and manage communication with board.
  */

/** \defgroup WriteFunc Board changes settings
  * Change settings on board.
  */

/** \defgroup ReadFunc Board reads settings
  * Retrieve current settings from board.
  */


/** \defgroup PartNumber Board identifications
  * Functions to retrieve identifications from board : Type, Serial....<br>
  */

/** \defgroup BoardStatus Retrieve board status
  * Monitor important status from board.
  */

/** \defgroup CalibFunc Board calibration
  * Retrieve or update board calibration.
  */

/** \defgroup ControlFunc Advanced board operations
  * Enable or disable some modes.<br>
  * Make current settings default settings.
  */

/** \defgroup LowLevel Direct Register Access
  * Low level function to access board registers.
  */

/** \defgroup CodeRange Code Range
  * Set of usefull defines.
  */


#ifdef COMCASP_LIBRARY
#define COMCASP_API __declspec(dllexport)
#else
#define COMCASP_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" { /* using a C++ compiler */
#endif

#include <stdio.h>

/** \addtogroup CodeRange
  * define Limits for Focus Voltage. */
/** @{ */
#define FOCUS_VOLTAGE_DIAL_MIN 20.0 /**< Focus Voltage display low value */
#define FOCUS_VOLTAGE_MIN 20.0F /**< Focus Voltage Low value */
#define FOCUS_VOLTAGE_MAX 70.0 /**< Focus Voltage High value */

//! @}


/** \addtogroup LowLevel
  * Define Name for register addresses. */
/** @{ */
#define REG_FOCUS_LSB 0x00 /**< Focus LSB address*/
#define REG_FOCUS_MSB 0x01 /**< Focus MSB address*/

#define REG_CONTROL 0x02 /**< Control address*/

//#define RCB_
#define REG_MODE 0x03 /**< Mode address*/

#define REG_PARTNUMBER 0x04 /**< Part number address*/
#define REG_VERSION 0x05 /**< Version address*/

#define REG_SERIAL_NUMBER 0x06 /**< Serial Number address*/
#define REG_SERIAL_NUMBER_LEN 8

#define REG_FAULT_REG 0x0E /**< Fault Register*/
#define REG_FOCAL_LENGTH 0x0F /**< Focal Length*/

#define REG_ADC_TEMPERATURE 0x10 /**< ADC Temperature */
#define REG_TEMPERATURE_INT 0x11 /**< Temperature integer part*/
#define REG_TEMPERATURE_DEC 0x12 /**< Temperature decimal part*/

#define REG_AS0 0x13 /**< As0*/
#define REG_AS1 0x16 /**< As1*/
#define REG_AS2 0x19 /**< As2*/

#define REG_BS0 0x1C /**< Bs0*/
#define REG_BS1 0x1F /**< Bs1*/
#define REG_BS2 0x22 /**< Bs2*/

#define REG_CS0 0x25 /**< CS0*/
#define REG_CS1 0x28 /**< CS1*/
#define REG_CS2 0x2B /**< CS2*/

#define REG_OL_CTRL 0x2E /**< OL_Ctrl*/
/* REG OL CTRL BITS */
#define ROLCB_THERMAL_COMP_ENABLE       0
#define ROLCB_SAVE_OL_CALIBRATION       1
#define ROLCB_FULL_THERMAL_CAL          2
#define ROLCB_CUSTOM_THERMAL_MODEL      3
#define ROLCB_PARTIAL_THERMAL_CAL       4

#define REG_LENS_OP_PWR 0x2F /**< Lens Optical Power*/

#define REG_T0 0x32 /**< T0*/
#define REG_P0 0x35 /**< P0*/
#define REG_P1 0x38 /**< P1*/
#define REG_V0 0x3B /**< V0*/
#define REG_V1 0x3E /**< V1*/
#define REG_V2 0x42 /**< V2*/

#define REG_S123_0 0x44 /**< S123[0]*/
#define REG_S123_1 0x47 /**< S123[1]*/
#define REG_S123_2 0x4A /**< S123[2]*/

#define REG_NEW_VOLT_COMMAND 0x4D /**< New Voltage Command*/
#define REG_TEMPERATURE 0x4E /**< Float Temperature*/
#define REG_TH_Comp 0x51 /**< TH_Comp*/
#define REG_NEW_OPTICAL_PWR_CMD 0x52 /**< New Optical Power command*/

#define REG_FLOAT_SIZE 3

#if 0
#define REG_SLOPE0 0x0B /**< Slope TA LSB address*/
#define REG_SLOPE1 0x0C /**< Slope TA address*/
#define REG_SLOPE2 0x0D /**< Slope TA address*/
#define REG_SLOPE3 0x0E /**< Slope TA MSB address*/

#define REG_V0D0 0x0F /**< V0D TA LSB address*/
#define REG_V0D1 0x10 /**< V0D TA address*/
#define REG_V0D2 0x11 /**< V0D TA address*/
#define REG_V0D3 0x12 /**< V0D TA MSB address*/

#define REG_TEMP_S_A0 0x13 /**< Temp S A LSB address*/
#define REG_TEMP_S_A1 0x14 /**< Temp S A address*/
#define REG_TEMP_S_A2 0x15 /**< Temp S A address*/
#define REG_TEMP_S_A3 0x16 /**< Temp S A MSB address*/

#define REG_TEMP_S_B0 0x17 /**< Temp S B LSB address*/
#define REG_TEMP_S_B1 0x18 /**< Temp S B address*/
#define REG_TEMP_S_B2 0x19 /**< Temp S B address*/
#define REG_TEMP_S_B3 0x1A /**< Temp S B MSB address*/

#define REG_TEMP_S_C0 0x1B /**< Temp S C LSB address*/
#define REG_TEMP_S_C1 0x1C /**< Temp S C address*/
#define REG_TEMP_S_C2 0x1D /**< Temp S C address*/
#define REG_TEMP_S_C3 0x1E /**< Temp S C MSB address*/

#define REG_TEMP_V_A0 0x1F /**< Temp V A LSB address*/
#define REG_TEMP_V_A1 0x20 /**< Temp V A address*/
#define REG_TEMP_V_A2 0x21 /**< Temp V A address*/
#define REG_TEMP_V_A3 0x22 /**< Temp V A MSB address*/

#define REG_TEMP_V_B0 0x23 /**< Temp V B LSB address */
#define REG_TEMP_V_B1 0x24 /**< Temp V B address */
#define REG_TEMP_V_B2 0x25 /**< Temp V B address */
#define REG_TEMP_V_B3 0x26 /**< Temp V B MSB address */

#define REG_TEMP_V_C0 0x27 /**< Temp V C LSB address */
#define REG_TEMP_V_C1 0x28 /**< Temp V C address */
#define REG_TEMP_V_C2 0x29 /**< Temp V C address */
#define REG_TEMP_V_C3 0x2A /**< Temp V C MSB address */

#define REG_TEMP_KEY1 0x3D /**< Key 1 address */
#define REG_TEMP_KEY2 0x3E /**< Key 2 address */

#define REG_PART_DESC 0x3F /**< Part description string (Size 25) address */

#define PART_DESC_LEN 25 /**< Part description string size expected */
#endif
//! @}


/** \addtogroup ComFunc
  * \ref eCOMCaspErr is return by most functions as a return of execution.
  * \see Casp_GetErrorMsg() to convert code to string
  @{ */
COMCASP_API typedef enum
{    eCaspSuccess=0, /**< Function call success. */
            eCaspTimeOut, /**< Timeout occur before completion. */
            eCaspCmdFailed, /**< Command failed. */
            eCaspNACKResponse, /**< Wrong response from command. */
            eCaspNotFound, /**< Board not found at call Casp_OpenCOM(). */
            eCaspNotConnected, /**< Not connected to Board (call Casp_OpenCOM() first). */
            eCaspOutOfRange, /**< Parameter out of range. */
            eCaspCRCErr, /**< CRC Error. */
            eCaspWriteErr, /**< Error while writing to serial port. */
            eCaspResponseIncomplete, /**< Response incomplete. */
            eCaspErrTotal
} eCOMCaspErr;
/** @} */

/** \addtogroup ComFunc
  * First call must be Casp_OpenCOM() or Casp_OpenCOMIdx(), last one Casp_CloseCOM().<br>
  * Retrieve user friendly message from \ref eCOMCaspErr with Casp_GetErrorMsg()<br>.
  * In case of manual COM port selection, use Casp_SysCOMCount() for available COM port on current system.<br>
  * Casp_SysCOMName() provides individual convenient name for each available port, Casp_SysCOMNames() provides name for every ports.
  * @{ */
/** Max COM port supported */
#define MAX_PORT_NUMBER 20
/** Open Communication with board. */
COMCASP_API eCOMCaspErr Casp_OpenCOM();
/** Open Communication with board on a given COM port index. */
COMCASP_API eCOMCaspErr Casp_OpenCOMIdx(int paIdxPort);
/** Close Communication with board. */
COMCASP_API eCOMCaspErr Casp_CloseCOM();
/** Query system COM port count. */
COMCASP_API int Casp_SysCOMCount();
/** Query system COM port name by index.
* \param paIdxPort COM port index. \see Casp_SysCOMCount().
* \return Pointer to COM name, of NULL if error.  */
COMCASP_API const char* Casp_SysCOMName(int paIdxPort);
/** Query system COM port names.
* \param paCOMArray array of strings. Use define MAX_PORT_NUMBER for initial size.
* \param paSize Effective string in array.
* \see Casp_SysCOMCount() for array size.
* \note Array's string are internal. No need to free them. */
COMCASP_API void Casp_SysCOMNames(const char *paCOMArray[MAX_PORT_NUMBER], int *paSize);
/** Retrieve String from execution code.
    \param eErr Execution code return by a previous functions.
    \see eCOMCaspErr */
COMCASP_API const char* Casp_GetErrorMsg( eCOMCaspErr eErr );
//! @}

/** \addtogroup WriteFunc
  * Set Focus voltage.<br>
  *
  * \ref Casp_SetFocusCalibration() provide access to calibration settings.<br>
  * Function return \ref eCOMCaspErr on completion.
  * @{ */

/** Set Focus voltage
  * \param paFocus Set focus voltage (range from 24 Vrms to 70 Vrms) */
COMCASP_API eCOMCaspErr Casp_SetFocusVoltage(double paFocus);

/** @} */

/** Set the Optical Power for the Optical power command
 * \param paOpticalPower float value to set optical power command register */
COMCASP_API eCOMCaspErr Casp_SetOpticalPower(float paOpticalPower);

/** Get the current Optical Power from the Optical power command
 * \param paOpticalPower pointer to the float variable read back Optical power command register */
COMCASP_API eCOMCaspErr Casp_GetOpticalPower(float *paOpticalPower);

/** \addtogroup ReadFunc
  * Retrieve current Focus voltage.<br>
  *
  * \ref Casp_GetFocusCalibration() provide access to calibration settings.<br>
  * Function return \ref eCOMCaspErr on completion.
  * @{ */

/** Read focus voltage.
  * \return paVoltage Focus Voltage (range from 24 Vrms to 70 Vrms) */
COMCASP_API eCOMCaspErr Casp_GetFocusVoltage(double* paVoltage);

/** @} */


/** @} */



/** \addtogroup PartNumber
  * This set of function provides functions to retrieve :<br>
  * \li Part Number.
  * \li Part Description.
  * \li Module Type.
  * \li Software version
  * \li Serial Number.
  *
  * Functions return \ref eCOMCaspErr on completion.
  *
  * @{ */

/** Read part number. This part number is use by \ref Casp_GetModuleType() for more precise details.<br>
  * \param[out] paPartNumber Part number, from 1 to 5, or 255. \see Casp_GetPartDescription(). */
COMCASP_API eCOMCaspErr Casp_GetPartNumber(unsigned char* paPartNumber);

/** Read Part description string from bard. This string is 25 char length. It's available when part number is 255.<br>
  * \param[out] paDescription Part description from board.
  * \param[in] paLen paDescription buffer size.*/
//COMCASP_API eCOMCaspErr Casp_GetPartDescription(char* paDescription, int paLen);

/** User friendly module type string. Use \ref Casp_GetPartNumber() and \ref Casp_GetPartDescription().<br>
  * \param[out] paModuleType Module type string for user display.
  * \param[in] paLen paModuleType buffer size. */
COMCASP_API eCOMCaspErr Casp_GetModuleType(char* paModuleType, size_t paLen);

/** User friendly string describing the operating mode<br>
 * \param[out] paModeString Operating Mode String.
 * \param[in] paLen paModuleType buffer size. */
COMCASP_API eCOMCaspErr Casp_GetModeString(char * paModeString, size_t paLen);

/** Read Software version from board.<br>
  * \param[out] paVersion Software version single value.*/
COMCASP_API eCOMCaspErr Casp_GetSWVersion(unsigned char *paVersion);

/** Read Focal length from the board board.<br>
  * \param[out] paFocalLength decimal value of focal lenght in millimeters.*/
COMCASP_API eCOMCaspErr Casp_GetFocalLength(unsigned char* paFocalLength);

/** Read module serial number.<br>
  * \param[out] paSerialNumber Module Serial number.
  * \param[in]  paLen Length of the paSerialNumber buffer.
*/
COMCASP_API eCOMCaspErr Casp_GetModuleSerialNumber(char * paBatchNumber, size_t paLen);

/** @} */

/** \addtogroup BoardStatus
  * Retrieve status from board.<br>
  * Function return \ref eCOMCaspErr on completion.
  * @{ */

/** Read current temperature
  * \return paTemperature Board's temperature.*/
COMCASP_API eCOMCaspErr Casp_GetTemperature(float* paTemperature);

/** @} */




/** \addtogroup ControlFunc
  * \ref Casp_StandbyEnable() enable or disable standby mode,
  * while \ref Casp_SetStandby() set or unset standby mode.<br>
  * Temperation compensation is enable by Casp_SetTemperatureCompensation(),
  * \ref Casp_TemperatureCompensationEnable() enable or disable this feature.<br>
  * \ref Casp_StoreRegister() make current board setting default settings.<br>
  * Function return \ref eCOMCaspErr on completion.
  * @{ */

/** Read Standby status.
  * \return paStandby Standby enable (1) or disable (0).*/
COMCASP_API eCOMCaspErr Casp_StandbyEnable(unsigned char* paStandby);

/** Set Standby mode.
  * \param paStandby Disable standby (0), or enable (1).*/
COMCASP_API eCOMCaspErr Casp_SetStandby(unsigned char paStandby);

/** Make current settings default settings.<br>
    Store current settings into EEPROM, make them default settings.
    \warning This function only return when EPROM write is completed.
*/
COMCASP_API eCOMCaspErr Casp_StoreRegister();

/** Query temperature compensation state.
  * \param[out] paEnable Compensation disable (0), or enable (1). */
COMCASP_API eCOMCaspErr Casp_GetThermalCompensation(unsigned char* paEnable);

/** Set temperature compensation.
  * \param paEnable Enable temperature compensation (1) or disable (0). */
COMCASP_API eCOMCaspErr Casp_SetThermalCompensation(unsigned char paEnable);

/** Query the Custom Thermal Calibration Model state.
  * \param[out] paEnable Compensation disable (0), or enable (1). */
COMCASP_API eCOMCaspErr Casp_GetCustomThermalCal(unsigned char* paEnable);


/** Set Custom Thermal Calibration Model Enable.
  * \param enableCustomModel Enable Custom Thermal model (1) or disable (0). */
COMCASP_API eCOMCaspErr Casp_SetCustomThermalCal(unsigned char paEnable);

/** Set Custom Thermal Calibration Model Enable.
  * \param enableCustomModel Enable Custom Thermal model (1) or disable (0).
  * \param isFullThermal Set the Full Thermal Calibration flag (1) or (0). */
COMCASP_API eCOMCaspErr Casp_SetOpenLoopControl(unsigned char enableCustomModel, unsigned char isFullThermalCal, unsigned char isPartialThermalCal);

/** Query the Full Thermal Calibration performed bit.
  * \param[out] paState full cal performed bit, true(1) or false (0). */
COMCASP_API eCOMCaspErr Casp_GetFullThermalCal(unsigned char* paState);

/** Set the Full Thermal Calibration performed bit.
  * \param[out] paState Partial cal performed bit, true(1) or false (0). */
COMCASP_API eCOMCaspErr Casp_SetFullThermalCal(unsigned char paState);


/** Query the Partial Thermal Calibration performed bit.
  * \param[out] paState Partial cal performed bit, true(1) or false (0). */
COMCASP_API eCOMCaspErr Casp_GetPartialThermalCal(unsigned char* paState);

/** Set the Partial Thermal Calibration performed bit.
  * \param[out] paState full cal performed bit, true(1) or false (0). */
COMCASP_API eCOMCaspErr Casp_SetPartialThermalCal(unsigned char paState);


/** Save the OL Calibration parameters. Automatically sets the Custom Thermal Cal flag.
 *  \param isFullThermal Set the Full Thermal Calibration flag (1) or (0).
 **/
COMCASP_API eCOMCaspErr Casp_SaveOLCalibration(bool isCustomCal, bool isFullThermalCal, bool isPartialThermalCal);

/** @} */

/** \addtogroup LowLevel
  * Set of function for registers access. See documentation for registers map. Registers are unsigned 8bit.
  * Read single register value with Casp_ReadAddress().<br>
  * Write single register value with Casp_WriteAddress().<br>
  * To write several registers in a row, use Casp_WriteAddressArray().<br><br>
  * All functions return \ref eCOMCaspErr on completion.
  * @{ */

/** Read register value by address.
    \param paAddr Register adress.
    \param paValue Register's value read. */
COMCASP_API eCOMCaspErr Casp_ReadAddress(unsigned char paAddr, unsigned char* paValue);

/** Read array of registers by address.
    \param paAddr Register adress.
    \param paArray Storage array for values to read.
    \param paArraySize Number of value to read. */
COMCASP_API eCOMCaspErr Casp_ReadAddressArray(unsigned char paAddr, unsigned char* paArray, unsigned char paArraySize);

/** Read float value from register area by address.
  \warning Use this function only on float type registers group.
    \param paAddr Register start adress (LSB).
    \param paValue Register's value read. */
COMCASP_API eCOMCaspErr Casp_ReadFloatAddress(unsigned char paAddr, float* paValue);

/** Write register single value by address.
    \param paAddr Register adress.
    \param paValue Register's value to write. */
COMCASP_API eCOMCaspErr Casp_WriteAddress(unsigned char paAddr, unsigned char paValue);

/** Write array of values at a starting address.
    \param paAddr First register address.
    \param paArray Array of values to write.
    \param paArraySize Number of value to write. */
COMCASP_API eCOMCaspErr Casp_WriteAddressArray(unsigned char paAddr, unsigned char* paArray, unsigned char paArraySize);

/** Write float value to register area by address.
  \warning Use this function only on float type registers group.
    \param paAddr Register start adress (LSB).
    \param paValue Register's value to write. */
COMCASP_API eCOMCaspErr Casp_WriteFloatAddress(unsigned char paAddr, float paValue);

/** @} */



#ifdef __cplusplus
   }
#endif

/*! \mainpage ComCasp - Communication with Caspian board
 *
 * \section intro_sec Introduction
 *
 * Varioptic provides a set of functions in a DLL to communicate with Caspian Board.<br>
 * This DLL allows customers to use its own programming language (C ...) or tool (Labview ...)
 *
 * \section install_sec Installation
 *
 * DLL require Microsoft Windows XP/Vista/Seven/8 32/64 bit operating system.<br>
 * Caspian board must be properly installed on system, and must be seen as a virtual Serial port.
 *
 * \section Version
 *
 * Current Version is 1.2.<br>
 *
 * See \ref revision for version history.
 *
 * \section overview DLL Overview
 *
 * DLL provides some sub-set of functions :<br>
 * - \ref ComFunc.
 * - \ref WriteFunc or \ref ReadFunc.
 * - \ref PartNumber.
 * - \ref BoardStatus.
 * - \ref CalibFunc.
 * - \ref ControlFunc.
 * - \ref CodeRange.
 * - \ref LowLevel.
 *
 * \section basic_use Connection
 *
 * DLL is fairly simple to use.<br>
 * Once board plugged, the first call must be Casp_OpenCOM().<br>
 * This function will search for connected board on workstation. Once board is found, function return \ref eCaspSuccess.<br>
 * Most functions return an \ref eCOMCaspErr code to indicate if completion was successfull or not.<br>
 * \ref eCOMCaspErr code can be converted to a string using Casp_GetErrorMsg() function.<br>
 *
 * Once communication is no more needed, Casp_CloseCOM() must be call for cleanup.<br>
 *
 * \section read_write Change Settings
 *
 * Once connection is etablish, Board settings may be changed.<br>
 * To change Focus base on Voltage value, see Casp_SetFocusVoltage().<br>
 * Or, change Focus base on distance with Casp_SetFocusDistance().<br>
 *
 * Retrieve current settings using \ref ReadFunc functions.
 * <br>
 *
 * \section do_calibration Calibration
 *
 * To improve board performance, a calibration settings may be update.
 * \see CalibFunc for more details about this feature.
 *
 * \section lowlevel_functions Registers access
 *
 * Using Registers map, this set of function allow low level access on board. Use with caution.<br>
 * See \ref LowLevel.
 */

/*! \page revision DLL Revision - History
 *
 * \Suppression of function related to old open loop model 
 * \section version121 Version 1.2.1
 *
 * \li Internal update of temperature computation.
 *
 * \section version12 Version 1.2
 *
 * \li Clean-up after temperature compensation upgrade.
 *
 * \section version11 Version 1.1
 *
 * \li Fix after integration.
 *
 * \section version10 Version 1.0
 *
 * \li Initial public release.
 *
 */

#endif // __COMCasp_H__

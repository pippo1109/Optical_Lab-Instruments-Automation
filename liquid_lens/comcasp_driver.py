"""
comcasp_driver.py

"""

import ctypes
import os
import sys
from typing import Optional, List, Tuple


# ---------------------------------------------------------------------------
# Constantes extraídas do ComCasp.h
# ---------------------------------------------------------------------------

MAX_PORT_NUMBER = 20

# Limites de tensão de foco [Vrms]
FOCUS_VOLTAGE_MIN  = 20.0
FOCUS_VOLTAGE_MAX  = 70.0

# Endereços de registradores (mapa de memória da placa)
REG_FOCUS_LSB           = 0x00
REG_FOCUS_MSB           = 0x01
REG_CONTROL             = 0x02
REG_MODE                = 0x03
REG_PARTNUMBER          = 0x04
REG_VERSION             = 0x05
REG_SERIAL_NUMBER       = 0x06
REG_SERIAL_NUMBER_LEN   = 8
REG_FAULT_REG           = 0x0E
REG_FOCAL_LENGTH        = 0x0F
REG_ADC_TEMPERATURE     = 0x10
REG_TEMPERATURE_INT     = 0x11
REG_TEMPERATURE_DEC     = 0x12
REG_AS0                 = 0x13
REG_AS1                 = 0x16
REG_AS2                 = 0x19
REG_BS0                 = 0x1C
REG_BS1                 = 0x1F
REG_BS2                 = 0x22
REG_CS0                 = 0x25
REG_CS1                 = 0x28
REG_CS2                 = 0x2B
REG_OL_CTRL             = 0x2E
REG_LENS_OP_PWR         = 0x2F
REG_T0                  = 0x32
REG_P0                  = 0x35
REG_P1                  = 0x38
REG_V0                  = 0x3B
REG_V1                  = 0x3E
REG_V2                  = 0x42
REG_S123_0              = 0x44
REG_S123_1              = 0x47
REG_S123_2              = 0x4A
REG_NEW_VOLT_COMMAND    = 0x4D
REG_TEMPERATURE         = 0x4E
REG_TH_Comp             = 0x51
REG_NEW_OPTICAL_PWR_CMD = 0x52
REG_FLOAT_SIZE          = 3

# Bits do registrador REG_OL_CTRL
ROLCB_THERMAL_COMP_ENABLE   = 0
ROLCB_SAVE_OL_CALIBRATION   = 1
ROLCB_FULL_THERMAL_CAL      = 2
ROLCB_CUSTOM_THERMAL_MODEL  = 3
ROLCB_PARTIAL_THERMAL_CAL   = 4

# Enum eCOMCaspErr → mapeado como inteiros (c_int no ctypes)
eCaspSuccess             = 0
eCaspTimeOut             = 1
eCaspCmdFailed           = 2
eCaspNACKResponse        = 3
eCaspNotFound            = 4
eCaspNotConnected        = 5
eCaspOutOfRange          = 6
eCaspCRCErr              = 7
eCaspWriteErr            = 8
eCaspResponseIncomplete  = 9
eCaspErrTotal            = 10

ERROR_NAMES = {
    eCaspSuccess            : "eCaspSuccess — Sucesso",
    eCaspTimeOut            : "eCaspTimeOut — Timeout",
    eCaspCmdFailed          : "eCaspCmdFailed — Comando falhou",
    eCaspNACKResponse       : "eCaspNACKResponse — Resposta inválida",
    eCaspNotFound           : "eCaspNotFound — Placa não encontrada",
    eCaspNotConnected       : "eCaspNotConnected — Não conectado (chame open() primeiro)",
    eCaspOutOfRange         : "eCaspOutOfRange — Parâmetro fora do range",
    eCaspCRCErr             : "eCaspCRCErr — Erro de CRC",
    eCaspWriteErr           : "eCaspWriteErr — Erro de escrita na porta serial",
    eCaspResponseIncomplete : "eCaspResponseIncomplete — Resposta incompleta",
}


def casp_error_str(code: int) -> str:
    return ERROR_NAMES.get(code, f"Erro desconhecido (código {code})")


class CaspError(Exception):
    """Exceção levantada quando uma função da DLL retorna != eCaspSuccess."""
    def __init__(self, fn: str, code: int):
        self.fn   = fn
        self.code = code
        super().__init__(f"{fn} → {casp_error_str(code)}")


# ---------------------------------------------------------------------------
# Classe principal
# ---------------------------------------------------------------------------

class CaspBoard:
    """
    Interface Python para a placa Varioptic Caspian (lente líquida).

    Uso básico:
    -----------
        board = CaspBoard("ComCasp64.dll")
        board.open()                        # conecta automaticamente
        board.set_focus_voltage(40.0)       # define tensão de foco [Vrms]
        v = board.get_focus_voltage()       # lê tensão atual
        t = board.get_temperature()         # lê temperatura da placa
        board.close()

    Context manager:
        with CaspBoard("ComCasp64.dll") as board:
            board.set_focus_voltage(35.0)
            print(board.get_temperature())

    Seleção manual de porta COM:
        ports = board.list_com_ports()
        board.open(port_index=2)            # abre COM3 (índice 2)
    """

    def __init__(self, dll_path: str = "ComCasp64.dll"):
        self.dll_path   = dll_path
        self._dll       = None
        self._connected = False

    # ------------------------------------------------------------------
    # Carregamento da DLL
    # ------------------------------------------------------------------

    def _load_dll(self):
        """Carrega a ComCasp64.dll e configura os protótipos de todas as funções."""
        if not os.path.isfile(self.dll_path):
            raise FileNotFoundError(
                f"DLL não encontrada: {self.dll_path}\n"
                "Certifique-se de que ComCasp64.dll está no mesmo diretório do script."
            )
        self._dll = ctypes.WinDLL(self.dll_path)
        self._configure_prototypes()
        print(f"DLL carregada: {self.dll_path}")

    def _configure_prototypes(self):
        dll = self._dll

        # --- Comunicação ---
        # eCOMCaspErr Casp_OpenCOM()
        dll.Casp_OpenCOM.argtypes = []
        dll.Casp_OpenCOM.restype  = ctypes.c_int

        # eCOMCaspErr Casp_OpenCOMIdx(int paIdxPort)
        dll.Casp_OpenCOMIdx.argtypes = [ctypes.c_int]
        dll.Casp_OpenCOMIdx.restype  = ctypes.c_int

        # eCOMCaspErr Casp_CloseCOM()
        dll.Casp_CloseCOM.argtypes = []
        dll.Casp_CloseCOM.restype  = ctypes.c_int

        # int Casp_SysCOMCount()
        dll.Casp_SysCOMCount.argtypes = []
        dll.Casp_SysCOMCount.restype  = ctypes.c_int

        # const char* Casp_SysCOMName(int paIdxPort)
        dll.Casp_SysCOMName.argtypes = [ctypes.c_int]
        dll.Casp_SysCOMName.restype  = ctypes.c_char_p

        # void Casp_SysCOMNames(const char* paCOMArray[MAX_PORT_NUMBER], int* paSize)
        dll.Casp_SysCOMNames.argtypes = [
            ctypes.POINTER(ctypes.c_char_p),
            ctypes.POINTER(ctypes.c_int),
        ]
        dll.Casp_SysCOMNames.restype = None

        # const char* Casp_GetErrorMsg(eCOMCaspErr eErr)
        dll.Casp_GetErrorMsg.argtypes = [ctypes.c_int]
        dll.Casp_GetErrorMsg.restype  = ctypes.c_char_p

        # --- Tensão de foco ---
        # eCOMCaspErr Casp_SetFocusVoltage(double paFocus)
        dll.Casp_SetFocusVoltage.argtypes = [ctypes.c_double]
        dll.Casp_SetFocusVoltage.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetFocusVoltage(double* paVoltage)
        dll.Casp_GetFocusVoltage.argtypes = [ctypes.POINTER(ctypes.c_double)]
        dll.Casp_GetFocusVoltage.restype  = ctypes.c_int

        # --- Potência óptica ---
        # eCOMCaspErr Casp_SetOpticalPower(float paOpticalPower)
        dll.Casp_SetOpticalPower.argtypes = [ctypes.c_float]
        dll.Casp_SetOpticalPower.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetOpticalPower(float* paOpticalPower)
        dll.Casp_GetOpticalPower.argtypes = [ctypes.POINTER(ctypes.c_float)]
        dll.Casp_GetOpticalPower.restype  = ctypes.c_int

        # --- Identificação ---
        # eCOMCaspErr Casp_GetPartNumber(unsigned char* paPartNumber)
        dll.Casp_GetPartNumber.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetPartNumber.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetModuleType(char* paModuleType, size_t paLen)
        dll.Casp_GetModuleType.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        dll.Casp_GetModuleType.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetModeString(char* paModeString, size_t paLen)
        dll.Casp_GetModeString.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        dll.Casp_GetModeString.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetSWVersion(unsigned char* paVersion)
        dll.Casp_GetSWVersion.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetSWVersion.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetFocalLength(unsigned char* paFocalLength)
        dll.Casp_GetFocalLength.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetFocalLength.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetModuleSerialNumber(char* paBatchNumber, size_t paLen)
        dll.Casp_GetModuleSerialNumber.argtypes = [ctypes.c_char_p, ctypes.c_size_t]
        dll.Casp_GetModuleSerialNumber.restype  = ctypes.c_int

        # --- Status ---
        # eCOMCaspErr Casp_GetTemperature(float* paTemperature)
        dll.Casp_GetTemperature.argtypes = [ctypes.POINTER(ctypes.c_float)]
        dll.Casp_GetTemperature.restype  = ctypes.c_int

        # --- Controle ---
        # eCOMCaspErr Casp_StandbyEnable(unsigned char* paStandby)
        dll.Casp_StandbyEnable.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_StandbyEnable.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetStandby(unsigned char paStandby)
        dll.Casp_SetStandby.argtypes = [ctypes.c_ubyte]
        dll.Casp_SetStandby.restype  = ctypes.c_int

        # eCOMCaspErr Casp_StoreRegister()
        dll.Casp_StoreRegister.argtypes = []
        dll.Casp_StoreRegister.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetThermalCompensation(unsigned char* paEnable)
        dll.Casp_GetThermalCompensation.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetThermalCompensation.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetThermalCompensation(unsigned char paEnable)
        dll.Casp_SetThermalCompensation.argtypes = [ctypes.c_ubyte]
        dll.Casp_SetThermalCompensation.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetCustomThermalCal(unsigned char* paEnable)
        dll.Casp_GetCustomThermalCal.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetCustomThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetCustomThermalCal(unsigned char paEnable)
        dll.Casp_SetCustomThermalCal.argtypes = [ctypes.c_ubyte]
        dll.Casp_SetCustomThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetOpenLoopControl(uchar, uchar, uchar)
        dll.Casp_SetOpenLoopControl.argtypes = [
            ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte
        ]
        dll.Casp_SetOpenLoopControl.restype = ctypes.c_int

        # eCOMCaspErr Casp_GetFullThermalCal(unsigned char* paState)
        dll.Casp_GetFullThermalCal.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetFullThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetFullThermalCal(unsigned char paState)
        dll.Casp_SetFullThermalCal.argtypes = [ctypes.c_ubyte]
        dll.Casp_SetFullThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_GetPartialThermalCal(unsigned char* paState)
        dll.Casp_GetPartialThermalCal.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        dll.Casp_GetPartialThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SetPartialThermalCal(unsigned char paState)
        dll.Casp_SetPartialThermalCal.argtypes = [ctypes.c_ubyte]
        dll.Casp_SetPartialThermalCal.restype  = ctypes.c_int

        # eCOMCaspErr Casp_SaveOLCalibration(bool, bool, bool)
        # bool em C é int no ctypes para compatibilidade com MSVC
        dll.Casp_SaveOLCalibration.argtypes = [
            ctypes.c_bool, ctypes.c_bool, ctypes.c_bool
        ]
        dll.Casp_SaveOLCalibration.restype = ctypes.c_int

        # --- Acesso direto a registradores (Low Level) ---
        # eCOMCaspErr Casp_ReadAddress(uchar paAddr, uchar* paValue)
        dll.Casp_ReadAddress.argtypes = [
            ctypes.c_ubyte, ctypes.POINTER(ctypes.c_ubyte)
        ]
        dll.Casp_ReadAddress.restype = ctypes.c_int

        # eCOMCaspErr Casp_ReadAddressArray(uchar paAddr, uchar* paArray, uchar paArraySize)
        dll.Casp_ReadAddressArray.argtypes = [
            ctypes.c_ubyte,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ubyte,
        ]
        dll.Casp_ReadAddressArray.restype = ctypes.c_int

        # eCOMCaspErr Casp_ReadFloatAddress(uchar paAddr, float* paValue)
        dll.Casp_ReadFloatAddress.argtypes = [
            ctypes.c_ubyte, ctypes.POINTER(ctypes.c_float)
        ]
        dll.Casp_ReadFloatAddress.restype = ctypes.c_int

        # eCOMCaspErr Casp_WriteAddress(uchar paAddr, uchar paValue)
        dll.Casp_WriteAddress.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte]
        dll.Casp_WriteAddress.restype  = ctypes.c_int

        # eCOMCaspErr Casp_WriteAddressArray(uchar paAddr, uchar* paArray, uchar paArraySize)
        dll.Casp_WriteAddressArray.argtypes = [
            ctypes.c_ubyte,
            ctypes.POINTER(ctypes.c_ubyte),
            ctypes.c_ubyte,
        ]
        dll.Casp_WriteAddressArray.restype = ctypes.c_int

        # eCOMCaspErr Casp_WriteFloatAddress(uchar paAddr, float paValue)
        dll.Casp_WriteFloatAddress.argtypes = [ctypes.c_ubyte, ctypes.c_float]
        dll.Casp_WriteFloatAddress.restype  = ctypes.c_int

        print("   Protótipos configurados ✔")

    # ------------------------------------------------------------------
    # Ciclo de vida da conexão
    # ------------------------------------------------------------------

    def open(self, port_index: Optional[int] = None):
        """
        Conecta à placa Caspian.

        port_index: None  → busca automática em todas as portas (recomendado)
                    int   → usa a porta COM de índice específico
        """
        if self._dll is None:
            self._load_dll()

        if port_index is None:
            ret = self._dll.Casp_OpenCOM()
        else:
            ret = self._dll.Casp_OpenCOMIdx(ctypes.c_int(port_index))

        self._check(ret, "Casp_OpenCOM")
        self._connected = True
        print("Conectado à placa Caspian!")

    def close(self):
        """Encerra a comunicação com a placa."""
        if self._dll and self._connected:
            self._dll.Casp_CloseCOM()
            self._connected = False
        print("Conexão encerrada.")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------
    # Descoberta de portas COM
    # ------------------------------------------------------------------

    def list_com_ports(self) -> List[str]:
        """
        Retorna a lista de nomes de portas COM disponíveis no sistema.
        Útil para seleção manual antes de chamar open(port_index=N).
        """
        if self._dll is None:
            self._load_dll()

        count = self._dll.Casp_SysCOMCount()
        ports = []
        for i in range(count):
            name = self._dll.Casp_SysCOMName(ctypes.c_int(i))
            if name:
                ports.append(name.decode())
        print(f"\n📡 Portas COM disponíveis ({count}):")
        for i, p in enumerate(ports):
            print(f"   [{i}] {p}")
        return ports

    def get_error_msg(self, code: int) -> str:
        """Converte um código eCOMCaspErr para string usando a própria DLL."""
        msg = self._dll.Casp_GetErrorMsg(ctypes.c_int(code))
        return msg.decode() if msg else f"código {code}"

    # ------------------------------------------------------------------
    # Identificação da placa
    # ------------------------------------------------------------------

    def get_part_number(self) -> int:
        """Retorna o número de parte (1–5 ou 255)."""
        val = ctypes.c_ubyte(0)
        self._check(self._dll.Casp_GetPartNumber(ctypes.byref(val)), "Casp_GetPartNumber")
        return val.value

    def get_module_type(self) -> str:
        """Retorna string amigável descrevendo o tipo de módulo."""
        buf = ctypes.create_string_buffer(64)
        self._check(self._dll.Casp_GetModuleType(buf, 64), "Casp_GetModuleType")
        return buf.value.decode()

    def get_mode_string(self) -> str:
        """Retorna string descrevendo o modo de operação atual."""
        buf = ctypes.create_string_buffer(64)
        self._check(self._dll.Casp_GetModeString(buf, 64), "Casp_GetModeString")
        return buf.value.decode()

    def get_sw_version(self) -> int:
        """Retorna a versão de firmware da placa."""
        val = ctypes.c_ubyte(0)
        self._check(self._dll.Casp_GetSWVersion(ctypes.byref(val)), "Casp_GetSWVersion")
        return val.value

    def get_focal_length(self) -> int:
        """Retorna o comprimento focal da lente em mm."""
        val = ctypes.c_ubyte(0)
        self._check(self._dll.Casp_GetFocalLength(ctypes.byref(val)), "Casp_GetFocalLength")
        return val.value

    def get_serial_number(self) -> str:
        """Retorna o número de série do módulo."""
        buf = ctypes.create_string_buffer(32)
        self._check(
            self._dll.Casp_GetModuleSerialNumber(buf, 32),
            "Casp_GetModuleSerialNumber"
        )
        return buf.value.decode()

    def print_info(self):
        """Imprime resumo das informações de identificação da placa."""
        print("\n Informações da placa Caspian:")
        print(f"Tipo de módulo    : {self.get_module_type()}")
        print(f"Número de parte   : {self.get_part_number()}")
        print(f"Número de série   : {self.get_serial_number()}")
        print(f"Versão firmware   : {self.get_sw_version()}")
        print(f"Comprimento focal : {self.get_focal_length()} mm")
        print(f"Modo operação     : {self.get_mode_string()}")

    # ------------------------------------------------------------------
    # Tensão de foco — controle principal da lente
    # ------------------------------------------------------------------

    def set_focus_voltage(self, voltage: float):
        """
        Define a tensão de foco da lente líquida.

        voltage: tensão em Vrms — range válido: 20.0 a 70.0 Vrms
                 tensões menores = foco mais próximo (maior dioptragem)
                 tensões maiores = foco mais distante (menor dioptragem)

        A DLL retorna eCaspOutOfRange se o valor estiver fora do range.
        """
        if not (FOCUS_VOLTAGE_MIN <= voltage <= FOCUS_VOLTAGE_MAX):
            raise ValueError(
                f"Tensão {voltage:.1f} Vrms fora do range "
                f"[{FOCUS_VOLTAGE_MIN}, {FOCUS_VOLTAGE_MAX}] Vrms"
            )
        self._check(
            self._dll.Casp_SetFocusVoltage(ctypes.c_double(voltage)),
            "Casp_SetFocusVoltage"
        )

    def get_focus_voltage(self) -> float:
        """Lê a tensão de foco atual em Vrms."""
        val = ctypes.c_double(0.0)
        self._check(
            self._dll.Casp_GetFocusVoltage(ctypes.byref(val)),
            "Casp_GetFocusVoltage"
        )
        return val.value

    # ------------------------------------------------------------------
    # Potência óptica
    # ------------------------------------------------------------------

    def set_optical_power(self, power: float):
        """
        Define a potência óptica da lente [dioptrias].
        Alternativa ao controle por tensão — usa calibração interna.
        """
        self._check(
            self._dll.Casp_SetOpticalPower(ctypes.c_float(power)),
            "Casp_SetOpticalPower"
        )

    def get_optical_power(self) -> float:
        """Lê a potência óptica atual [dioptrias]."""
        val = ctypes.c_float(0.0)
        self._check(
            self._dll.Casp_GetOpticalPower(ctypes.byref(val)),
            "Casp_GetOpticalPower"
        )
        return val.value

    # ------------------------------------------------------------------
    # Status da placa
    # ------------------------------------------------------------------

    def get_temperature(self) -> float:
        """Retorna a temperatura atual da placa em °C."""
        val = ctypes.c_float(0.0)
        self._check(
            self._dll.Casp_GetTemperature(ctypes.byref(val)),
            "Casp_GetTemperature"
        )
        return val.value

    # ------------------------------------------------------------------
    # Modo standby
    # ------------------------------------------------------------------

    def get_standby(self) -> bool:
        """Retorna True se o standby está ativo."""
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_StandbyEnable(ctypes.byref(val)),
            "Casp_StandbyEnable"
        )
        return bool(val.value)

    def set_standby(self, enable: bool):
        """Ativa (True) ou desativa (False) o modo standby."""
        self._check(
            self._dll.Casp_SetStandby(ctypes.c_ubyte(1 if enable else 0)),
            "Casp_SetStandby"
        )

    # ------------------------------------------------------------------
    # Compensação térmica
    # ------------------------------------------------------------------

    def get_thermal_compensation(self) -> bool:
        """Retorna True se a compensação térmica está habilitada."""
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_GetThermalCompensation(ctypes.byref(val)),
            "Casp_GetThermalCompensation"
        )
        return bool(val.value)

    def set_thermal_compensation(self, enable: bool):
        """Habilita (True) ou desabilita (False) a compensação térmica automática."""
        self._check(
            self._dll.Casp_SetThermalCompensation(ctypes.c_ubyte(1 if enable else 0)),
            "Casp_SetThermalCompensation"
        )

    def get_custom_thermal_cal(self) -> bool:
        """Retorna True se o modelo térmico customizado está ativo."""
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_GetCustomThermalCal(ctypes.byref(val)),
            "Casp_GetCustomThermalCal"
        )
        return bool(val.value)

    def set_custom_thermal_cal(self, enable: bool):
        """Habilita (True) ou desabilita (False) o modelo térmico customizado."""
        self._check(
            self._dll.Casp_SetCustomThermalCal(ctypes.c_ubyte(1 if enable else 0)),
            "Casp_SetCustomThermalCal"
        )

    def set_open_loop_control(
        self,
        enable_custom_model: bool,
        is_full_thermal_cal: bool,
        is_partial_thermal_cal: bool,
    ):
        """
        Configura o controle open-loop e flags de calibração térmica.

        enable_custom_model    : ativa modelo térmico customizado
        is_full_thermal_cal    : flag de calibração térmica completa
        is_partial_thermal_cal : flag de calibração térmica parcial
        """
        self._check(
            self._dll.Casp_SetOpenLoopControl(
                ctypes.c_ubyte(enable_custom_model),
                ctypes.c_ubyte(is_full_thermal_cal),
                ctypes.c_ubyte(is_partial_thermal_cal),
            ),
            "Casp_SetOpenLoopControl"
        )

    def get_full_thermal_cal(self) -> bool:
        """Retorna True se a calibração térmica completa foi realizada."""
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_GetFullThermalCal(ctypes.byref(val)),
            "Casp_GetFullThermalCal"
        )
        return bool(val.value)

    def set_full_thermal_cal(self, state: bool):
        """Define o bit de calibração térmica completa."""
        self._check(
            self._dll.Casp_SetFullThermalCal(ctypes.c_ubyte(state)),
            "Casp_SetFullThermalCal"
        )

    def get_partial_thermal_cal(self) -> bool:
        """Retorna True se a calibração térmica parcial foi realizada."""
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_GetPartialThermalCal(ctypes.byref(val)),
            "Casp_GetPartialThermalCal"
        )
        return bool(val.value)

    def set_partial_thermal_cal(self, state: bool):
        """Define o bit de calibração térmica parcial."""
        self._check(
            self._dll.Casp_SetPartialThermalCal(ctypes.c_ubyte(state)),
            "Casp_SetPartialThermalCal"
        )

    def save_ol_calibration(
        self,
        is_custom_cal: bool,
        is_full_thermal_cal: bool,
        is_partial_thermal_cal: bool,
    ):
        """
        Salva os parâmetros de calibração Open-Loop na placa.
        Define automaticamente o flag de Custom Thermal Cal.

        ⚠️  Operação de escrita em EEPROM — use com cuidado.
        """
        self._check(
            self._dll.Casp_SaveOLCalibration(
                ctypes.c_bool(is_custom_cal),
                ctypes.c_bool(is_full_thermal_cal),
                ctypes.c_bool(is_partial_thermal_cal),
            ),
            "Casp_SaveOLCalibration"
        )

    # ------------------------------------------------------------------
    # Persistência de configurações
    # ------------------------------------------------------------------

    def store_register(self):
        """
        Grava as configurações atuais na EEPROM da placa,
        tornando-as os valores padrão ao ligar.

        ⚠️  Bloqueante — só retorna quando a escrita na EEPROM termina.
        """
        print("💾 Gravando configurações na EEPROM...")
        self._check(self._dll.Casp_StoreRegister(), "Casp_StoreRegister")
        print("   Configurações gravadas ✔")

    # ------------------------------------------------------------------
    # Acesso direto a registradores (Low Level)
    # ------------------------------------------------------------------

    def read_register(self, addr: int) -> int:
        """
        Lê um registrador de 8 bits pelo endereço.

        addr: endereço do registrador (use as constantes REG_*)
        Retorna: valor lido (0–255)
        """
        val = ctypes.c_ubyte(0)
        self._check(
            self._dll.Casp_ReadAddress(ctypes.c_ubyte(addr), ctypes.byref(val)),
            "Casp_ReadAddress"
        )
        return val.value

    def read_register_array(self, addr: int, count: int) -> List[int]:
        """
        Lê um array de `count` registradores consecutivos a partir de `addr`.
        Retorna lista de inteiros (0–255).
        """
        buf = (ctypes.c_ubyte * count)()
        self._check(
            self._dll.Casp_ReadAddressArray(
                ctypes.c_ubyte(addr), buf, ctypes.c_ubyte(count)
            ),
            "Casp_ReadAddressArray"
        )
        return list(buf)

    def read_float_register(self, addr: int) -> float:
        """
        Lê um valor float (3 bytes) a partir do endereço especificado.
        Use apenas em regiões de registradores do tipo float (ex: REG_AS0, REG_T0...).
        """
        val = ctypes.c_float(0.0)
        self._check(
            self._dll.Casp_ReadFloatAddress(ctypes.c_ubyte(addr), ctypes.byref(val)),
            "Casp_ReadFloatAddress"
        )
        return val.value

    def write_register(self, addr: int, value: int):
        """
        Escreve um valor (0–255) em um registrador de 8 bits.

        ⚠️  Acesso direto — use com cautela. Consulte o mapa de registradores.
        """
        self._check(
            self._dll.Casp_WriteAddress(ctypes.c_ubyte(addr), ctypes.c_ubyte(value)),
            "Casp_WriteAddress"
        )

    def write_register_array(self, addr: int, values: List[int]):
        """
        Escreve um array de valores a partir do endereço `addr`.

        values: lista de inteiros (0–255)
        """
        arr = (ctypes.c_ubyte * len(values))(*values)
        self._check(
            self._dll.Casp_WriteAddressArray(
                ctypes.c_ubyte(addr), arr, ctypes.c_ubyte(len(values))
            ),
            "Casp_WriteAddressArray"
        )

    def write_float_register(self, addr: int, value: float):
        """
        Escreve um valor float em uma região de registradores float.
        Use apenas nos endereços corretos (REG_AS0, REG_T0, etc.).

        ⚠️  Acesso direto — afeta calibração. Use com extrema cautela.
        """
        self._check(
            self._dll.Casp_WriteFloatAddress(ctypes.c_ubyte(addr), ctypes.c_float(value)),
            "Casp_WriteFloatAddress"
        )

    def dump_registers(self, start: int = 0x00, end: int = 0x55) -> dict:
        """
        Lê todos os registradores no range [start, end] e retorna um dicionário
        {endereço_hex: valor}. Útil para diagnóstico e debug.
        """
        result = {}
        for addr in range(start, end + 1):
            try:
                result[addr] = self.read_register(addr)
            except CaspError:
                result[addr] = None
        return result

    def print_register_dump(self, start: int = 0x00, end: int = 0x55):
        """Imprime dump formatado dos registradores."""
        regs = self.dump_registers(start, end)
        print(f"\n🗂️  Dump de registradores [0x{start:02X}–0x{end:02X}]:")
        for addr, val in regs.items():
            label = _REG_NAMES.get(addr, "")
            if val is not None:
                print(f"   0x{addr:02X}  {val:3d}  0x{val:02X}  {label}")
            else:
                print(f"   0x{addr:02X}  ---  erro na leitura")

    # ------------------------------------------------------------------
    # Utilitários internos
    # ------------------------------------------------------------------

    def _check(self, ret: int, fn_name: str):
        if ret != eCaspSuccess:
            raise CaspError(fn_name, ret)

    @property
    def is_connected(self) -> bool:
        return self._connected


# ---------------------------------------------------------------------------
# Mapa de nomes de registradores para o dump
# ---------------------------------------------------------------------------

_REG_NAMES = {
    REG_FOCUS_LSB           : "REG_FOCUS_LSB",
    REG_FOCUS_MSB           : "REG_FOCUS_MSB",
    REG_CONTROL             : "REG_CONTROL",
    REG_MODE                : "REG_MODE",
    REG_PARTNUMBER          : "REG_PARTNUMBER",
    REG_VERSION             : "REG_VERSION",
    REG_SERIAL_NUMBER       : "REG_SERIAL_NUMBER",
    REG_FAULT_REG           : "REG_FAULT_REG",
    REG_FOCAL_LENGTH        : "REG_FOCAL_LENGTH",
    REG_ADC_TEMPERATURE     : "REG_ADC_TEMPERATURE",
    REG_TEMPERATURE_INT     : "REG_TEMPERATURE_INT",
    REG_TEMPERATURE_DEC     : "REG_TEMPERATURE_DEC",
    REG_AS0                 : "REG_AS0",
    REG_AS1                 : "REG_AS1",
    REG_AS2                 : "REG_AS2",
    REG_BS0                 : "REG_BS0",
    REG_BS1                 : "REG_BS1",
    REG_BS2                 : "REG_BS2",
    REG_CS0                 : "REG_CS0",
    REG_CS1                 : "REG_CS1",
    REG_CS2                 : "REG_CS2",
    REG_OL_CTRL             : "REG_OL_CTRL",
    REG_LENS_OP_PWR         : "REG_LENS_OP_PWR",
    REG_T0                  : "REG_T0",
    REG_P0                  : "REG_P0",
    REG_P1                  : "REG_P1",
    REG_V0                  : "REG_V0",
    REG_V1                  : "REG_V1",
    REG_V2                  : "REG_V2",
    REG_S123_0              : "REG_S123_0",
    REG_S123_1              : "REG_S123_1",
    REG_S123_2              : "REG_S123_2",
    REG_NEW_VOLT_COMMAND    : "REG_NEW_VOLT_COMMAND",
    REG_TEMPERATURE         : "REG_TEMPERATURE",
    REG_TH_Comp             : "REG_TH_Comp",
    REG_NEW_OPTICAL_PWR_CMD : "REG_NEW_OPTICAL_PWR_CMD",
}


# ---------------------------------------------------------------------------
# Exemplo de uso completo
# ---------------------------------------------------------------------------

def exemplo_completo():
    """
    Demonstração do fluxo completo de uso da placa Caspian.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DLL_PATH = os.path.join(BASE_DIR, "ComCasp64.dll")

    print("=" * 60)
    print("  Varioptic Caspian — Driver Python (ctypes)")
    print("  Guaxyn & Nox 🦝🔬")
    print("=" * 60)

    board = CaspBoard(DLL_PATH)

    try:
        # 1. Listar portas disponíveis
        ports = board.list_com_ports()

        # 2. Conectar automaticamente (busca em todas as portas)
        board.open()

        # 3. Informações de identificação
        board.print_info()

        # 4. Status inicial
        temp = board.get_temperature()
        print(f"\n🌡️  Temperatura da placa: {temp:.2f} °C")

        v_atual = board.get_focus_voltage()
        print(f"🔭 Tensão de foco atual: {v_atual:.2f} Vrms")

        # 5. Verificar modo standby
        em_standby = board.get_standby()
        print(f"💤 Standby: {'ativo' if em_standby else 'inativo'}")
        if em_standby:
            print("   Desativando standby...")
            board.set_standby(False)

        # 6. Verificar compensação térmica
        comp_termica = board.get_thermal_compensation()
        print(f"🌡️  Compensação térmica: {'ativa' if comp_termica else 'inativa'}")

        # 7. Varredura de tensão de foco
        print("\n📊 Varredura de tensão de foco (30 → 60 Vrms em 5 passos):")
        import time
        for v in [30.0, 37.5, 45.0, 52.5, 60.0]:
            board.set_focus_voltage(v)
            v_lido = board.get_focus_voltage()
            t_lido = board.get_temperature()
            print(f"   Set: {v:.1f} Vrms → Lido: {v_lido:.2f} Vrms | T={t_lido:.1f}°C")
            time.sleep(1.0)

        # 8. Controle por potência óptica
        print("\n🔬 Potência óptica atual:")
        op = board.get_optical_power()
        print(f"   {op:.4f} dioptrias")

        # 9. Leitura de registrador direto (exemplo: REG_MODE)
        mode_val = board.read_register(REG_MODE)
        fault_val = board.read_register(REG_FAULT_REG)
        print(f"\n🗂️  REG_MODE   (0x03) = 0x{mode_val:02X}")
        print(f"   REG_FAULT  (0x0E) = 0x{fault_val:02X}")

        # 10. Leitura de float de calibração (coef. térmico As0)
        as0 = board.read_float_register(REG_AS0)
        print(f"   REG_AS0 (calib. térmica) = {as0:.6f}")

        # 11. Dump completo de registradores (opcional — comentar se não precisar)
        # board.print_register_dump(0x00, 0x55)

        # 12. Restaurar tensão neutra
        board.set_focus_voltage(45.0)
        print(f"\n✅ Tensão restaurada para 45.0 Vrms")

    except CaspError as e:
        print(f"\n❌ Erro Caspian: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        raise
    finally:
        board.close()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("⚠️  Este driver requer Windows com ComCasp64.dll instalada.")
        sys.exit(1)
    exemplo_completo()

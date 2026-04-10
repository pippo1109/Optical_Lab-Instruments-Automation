"""
SDK DLL : avaspecx64.dll (Windows x64)
"""

import ctypes
import ctypes.util
import time
import sys
import os
from typing import Optional, Tuple, List

sys.path.append(r'avaspec_3648/avaspecx64.dll')
dll_path = os.path.abspath(r'avaspec_3648/avaspecx64.dll')


# Constantes avaspec.h

USER_ID_LEN             = 64
AVS_SERIAL_LEN          = 10
MAX_TEMP_SENSORS        = 3
VERSION_LEN             = 16
DETECTOR_NAME_LEN       = 20
NR_WAVELEN_POL_COEF     = 5
NR_NONLIN_POL_COEF      = 8
MAX_VIDEO_CHANNELS      = 2
NR_DEFECTIVE_PIXELS     = 30
MAX_NR_PIXELS           = 4096
NR_TEMP_POL_COEF        = 5
NR_DAC_POL_COEF         = 2
OEM_DATA_LEN            = 4096
CLIENT_ID_SIZE          = 32
ETHSET_RES_SIZE         = 79

# Modos de trigger
SW_TRIGGER_MODE         = 0
HW_TRIGGER_MODE         = 1
SS_TRIGGER_MODE         = 2
EXTERNAL_TRIGGER        = 0
SYNC_TRIGGER            = 1
EDGE_TRIGGER_SOURCE     = 0
LEVEL_TRIGGER_SOURCE    = 1

# Pixels dark para o AvaSpec-3648 (sensor TCD1304)
TCD_FIRST_USED_DARK_PIXEL = 0
TCD_USED_DARK_PIXELS      = 12
TCD_TOTAL_DARK_PIXELS     = 13

# Tempo mínimo de integração ILX [ms]
MIN_ILX_INTTIME         = 1.1

INVALID_AVS_HANDLE_VALUE = 1000

# Códigos de retorno/erro
ERR_SUCCESS                   =  0
ERR_INVALID_PARAMETER         = -1
ERR_OPERATION_NOT_SUPPORTED   = -2
ERR_DEVICE_NOT_FOUND          = -3
ERR_INVALID_DEVICE_ID         = -4
ERR_OPERATION_PENDING         = -5
ERR_TIMEOUT                   = -6
ERR_INVALID_MEAS_DATA         = -8
ERR_INVALID_SIZE              = -9
ERR_INVALID_PIXEL_RANGE       = -10
ERR_INVALID_INT_TIME          = -11
ERR_INVALID_COMBINATION       = -12
ERR_NO_MEAS_BUFFER_AVAIL      = -14
ERR_UNKNOWN                   = -15
ERR_COMMUNICATION             = -16
ERR_NO_SPECTRA_IN_RAM         = -17
ERR_DLL_INITIALISATION        = -20
ERR_INVALID_STATE             = -21

ERROR_MESSAGES = {
    ERR_SUCCESS                 : "Sucesso",
    ERR_INVALID_PARAMETER       : "Parâmetro inválido",
    ERR_OPERATION_NOT_SUPPORTED : "Operação não suportada",
    ERR_DEVICE_NOT_FOUND        : "Dispositivo não encontrado",
    ERR_INVALID_DEVICE_ID       : "ID de dispositivo inválido",
    ERR_OPERATION_PENDING       : "Operação pendente",
    ERR_TIMEOUT                 : "Timeout",
    ERR_INVALID_MEAS_DATA       : "Dados de medição inválidos",
    ERR_INVALID_SIZE            : "Tamanho inválido",
    ERR_INVALID_PIXEL_RANGE     : "Range de pixels inválido",
    ERR_INVALID_INT_TIME        : "Tempo de integração inválido",
    ERR_NO_MEAS_BUFFER_AVAIL    : "Buffer de medição não disponível",
    ERR_COMMUNICATION           : "Erro de comunicação",
    ERR_NO_SPECTRA_IN_RAM       : "Sem espectros na RAM",
    ERR_DLL_INITIALISATION      : "Erro na inicialização da DLL",
}


def avs_error_str(code: int) -> str:
    return ERROR_MESSAGES.get(code, f"Erro desconhecido (código {code})")


# ---------------------------------------------------------------------------
# Estruturas C mapeadas para ctypes
# Atenção: #pragma pack(push,1) → sem padding entre campos!
# ---------------------------------------------------------------------------

class AvsIdentityType(ctypes.Structure):
    """Identificação do espectrômetro."""
    _pack_ = 1
    _fields_ = [
        ("SerialNumber",     ctypes.c_char * AVS_SERIAL_LEN),
        ("UserFriendlyName", ctypes.c_char * USER_ID_LEN),
        ("Status",           ctypes.c_uint8),
    ]

    def __repr__(self):
        return (f"AvsIdentity(serial={self.SerialNumber.decode()!r}, "
                f"name={self.UserFriendlyName.decode()!r}, status={self.Status})")


class DarkCorrectionType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Enable",           ctypes.c_uint8),
        ("m_ForgetPercentage", ctypes.c_uint8),
    ]


class SmoothingType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_SmoothPix",   ctypes.c_uint16),
        ("m_SmoothModel", ctypes.c_uint8),
    ]


class TriggerType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Mode",       ctypes.c_uint8),
        ("m_Source",     ctypes.c_uint8),
        ("m_SourceType", ctypes.c_uint8),
    ]


class ControlSettingsType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_StrobeControl",   ctypes.c_uint16),
        ("m_LaserDelay",      ctypes.c_uint32),
        ("m_LaserWidth",      ctypes.c_uint32),
        ("m_LaserWaveLength", ctypes.c_float),
        ("m_StoreToRam",      ctypes.c_uint16),
    ]


class MeasConfigType(ctypes.Structure):
    """Configuração de medição — coração do controle do espectrômetro."""
    _pack_ = 1
    _fields_ = [
        ("m_StartPixel",         ctypes.c_uint16),
        ("m_StopPixel",          ctypes.c_uint16),
        ("m_IntegrationTime",    ctypes.c_float),   # [ms]
        ("m_IntegrationDelay",   ctypes.c_uint32),
        ("m_NrAverages",         ctypes.c_uint32),
        ("m_CorDynDark",         DarkCorrectionType),
        ("m_Smoothing",          SmoothingType),
        ("m_SaturationDetection",ctypes.c_uint8),
        ("m_Trigger",            TriggerType),
        ("m_Control",            ControlSettingsType),
    ]


class DetectorType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_SensorType",         ctypes.c_uint8),
        ("m_NrPixels",           ctypes.c_uint16),
        ("m_aFit",               ctypes.c_float * NR_WAVELEN_POL_COEF),
        ("m_NLEnable",           ctypes.c_bool),
        ("m_aNLCorrect",         ctypes.c_double * NR_NONLIN_POL_COEF),
        ("m_aLowNLCounts",       ctypes.c_double),
        ("m_aHighNLCounts",      ctypes.c_double),
        ("m_Gain",               ctypes.c_float * MAX_VIDEO_CHANNELS),
        ("m_Reserved",           ctypes.c_float),
        ("m_Offset",             ctypes.c_float * MAX_VIDEO_CHANNELS),
        ("m_ExtOffset",          ctypes.c_float),
        ("m_DefectivePixels",    ctypes.c_uint16 * NR_DEFECTIVE_PIXELS),
    ]


class SmoothingTypeInner(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("m_SmoothPix", ctypes.c_uint16), ("m_SmoothModel", ctypes.c_uint8)]


class SpectrumCalibrationType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Smoothing",      SmoothingTypeInner),
        ("m_CalInttime",     ctypes.c_float),
        ("m_aCalibConvers",  ctypes.c_float * MAX_NR_PIXELS),
    ]


class IrradianceType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_IntensityCalib",  SpectrumCalibrationType),
        ("m_CalibrationType", ctypes.c_uint8),
        ("m_FiberDiameter",   ctypes.c_uint32),
    ]


class SpectrumCorrectionType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("m_aSpectrumCorrect", ctypes.c_float * MAX_NR_PIXELS)]


class StandAloneType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Enable", ctypes.c_bool),
        ("m_Meas",   MeasConfigType),
        ("m_Nmsr",   ctypes.c_int16),
    ]


class DynamicStorageType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Nmsr",     ctypes.c_int32),
        ("m_Reserved", ctypes.c_uint8 * 8),
    ]


class TempSensorType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("m_aFit", ctypes.c_float * NR_TEMP_POL_COEF)]


class TecControlType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Enable",   ctypes.c_bool),
        ("m_Setpoint", ctypes.c_float),
        ("m_aFit",     ctypes.c_float * NR_DAC_POL_COEF),
    ]


class ProcessControlType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("AnalogLow",   ctypes.c_float * 2),
        ("AnalogHigh",  ctypes.c_float * 2),
        ("DigitalLow",  ctypes.c_float * 10),
        ("DigitalHigh", ctypes.c_float * 10),
    ]


class EthernetSettingsType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_IpAddr",        ctypes.c_uint32),
        ("m_NetMask",       ctypes.c_uint32),
        ("m_Gateway",       ctypes.c_uint32),
        ("m_DhcpEnabled",   ctypes.c_uint8),
        ("m_TcpPort",       ctypes.c_uint16),
        ("m_LinkStatus",    ctypes.c_uint8),
        ("m_ClientIdType",  ctypes.c_uint8),
        ("m_ClientIdCustom",ctypes.c_char * CLIENT_ID_SIZE),
        ("m_Reserved",      ctypes.c_uint8 * ETHSET_RES_SIZE),
    ]


class OemDataType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [("m_data", ctypes.c_uint8 * OEM_DATA_LEN)]


# Calcula SETTINGS_RESERVED_LEN dinamicamente (igual ao #define do header)
def _calc_settings_reserved_len() -> int:
    total = (
        ctypes.sizeof(ctypes.c_uint16) +   # m_Len
        ctypes.sizeof(ctypes.c_uint16) +   # m_ConfigVersion
        USER_ID_LEN +
        ctypes.sizeof(DetectorType) +
        ctypes.sizeof(IrradianceType) +
        ctypes.sizeof(SpectrumCalibrationType) +
        ctypes.sizeof(SpectrumCorrectionType) +
        ctypes.sizeof(StandAloneType) +
        ctypes.sizeof(DynamicStorageType) +
        ctypes.sizeof(TempSensorType) * MAX_TEMP_SENSORS +
        ctypes.sizeof(TecControlType) +
        ctypes.sizeof(ProcessControlType) +
        ctypes.sizeof(EthernetSettingsType) +
        ctypes.sizeof(ctypes.c_bool) +     # m_MessageAckDisable
        ctypes.sizeof(ctypes.c_bool) +     # m_IncludeCRC
        ctypes.sizeof(OemDataType) +
        ctypes.sizeof(ctypes.c_uint32)     # CRC firmware
    )
    return (62 * 1024) - total

SETTINGS_RESERVED_LEN = _calc_settings_reserved_len()


class DeviceConfigType(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m_Len",                ctypes.c_uint16),
        ("m_ConfigVersion",      ctypes.c_uint16),
        ("m_aUserFriendlyId",    ctypes.c_char * USER_ID_LEN),
        ("m_Detector",           DetectorType),
        ("m_Irradiance",         IrradianceType),
        ("m_Reflectance",        SpectrumCalibrationType),
        ("m_SpectrumCorrect",    SpectrumCorrectionType),
        ("m_StandAlone",         StandAloneType),
        ("m_DynamicStorage",     DynamicStorageType),
        ("m_aTemperature",       TempSensorType * MAX_TEMP_SENSORS),
        ("m_TecControl",         TecControlType),
        ("m_ProcessControl",     ProcessControlType),
        ("m_EthernetSettings",   EthernetSettingsType),
        ("m_MessageAckDisable",  ctypes.c_bool),
        ("m_IncludeCRC",         ctypes.c_bool),
        ("m_aReserved",          ctypes.c_uint8 * SETTINGS_RESERVED_LEN),
        ("m_OemData",            OemDataType),
    ]


# ---------------------------------------------------------------------------
# Classe principal: wrapper da DLL
# ---------------------------------------------------------------------------

class AvaSpec:
    """
    Interface Python para o espectrômetro AvaSpec-3648 via ctypes.

    Uso básico:
    -----------
        spec = AvaSpec("avaspecx64.dll")
        spec.init()
        spec.get_device_list()
        spec.activate(0)
        spec.configure(integration_time_ms=10.0, nr_averages=1)
        wavelengths, spectrum = spec.measure_single()
        spec.close()

    Ou como context manager:
        with AvaSpec("avaspecx64.dll") as spec:
            spec.get_device_list()
            spec.activate(0)
            wl, sp = spec.measure_single(integration_time_ms=50.0)
    """

    def __init__(self, dll_path: str = dll_path):
        self.dll_path   = dll_path
        self._dll       = None
        self._handle    = None   # AvsHandle (ctypes.c_long)
        self._n_pixels  = 0
        self._devices: List[AvsIdentityType] = []
        self._meas_cfg  = MeasConfigType()

    # ------------------------------------------------------------------
    # Carregamento da DLL e configuração de protótipos
    # ------------------------------------------------------------------

    def _load_dll(self):
        """Carrega a avaspecx64.dll e define os protótipos de cada função."""
        if not os.path.isfile(self.dll_path):
            raise FileNotFoundError(
                f"DLL não encontrada: {self.dll_path}\n"
                "Copie avaspecx64.dll para o mesmo diretório do script."
            )
        self._dll = ctypes.WinDLL(self.dll_path)
        self._configure_prototypes()
        print(f"✅ DLL carregada: {self.dll_path}")

    def _configure_prototypes(self):
        """Define argtypes e restype para cada função da DLL."""
        dll = self._dll

        # int AVS_Init(short a_Port)
        dll.AVS_Init.argtypes  = [ctypes.c_short]
        dll.AVS_Init.restype   = ctypes.c_int

        # int AVS_Done(void)
        dll.AVS_Done.argtypes  = []
        dll.AVS_Done.restype   = ctypes.c_int

        # int AVS_GetNrOfDevices(void)
        dll.AVS_GetNrOfDevices.argtypes = []
        dll.AVS_GetNrOfDevices.restype  = ctypes.c_int

        # int AVS_UpdateUSBDevices(void)
        dll.AVS_UpdateUSBDevices.argtypes = []
        dll.AVS_UpdateUSBDevices.restype  = ctypes.c_int

        # int AVS_GetList(uint a_ListSize, uint* a_pRequiredSize, AvsIdentityType* a_pList)
        dll.AVS_GetList.argtypes = [
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(AvsIdentityType),
        ]
        dll.AVS_GetList.restype = ctypes.c_int

        # AvsHandle AVS_Activate(AvsIdentityType* a_pDeviceId)
        dll.AVS_Activate.argtypes = [ctypes.POINTER(AvsIdentityType)]
        dll.AVS_Activate.restype  = ctypes.c_long

        # bool AVS_Deactivate(AvsHandle a_hDevice)
        dll.AVS_Deactivate.argtypes = [ctypes.c_long]
        dll.AVS_Deactivate.restype  = ctypes.c_bool

        # int AVS_PrepareMeasure(AvsHandle, MeasConfigType*)
        dll.AVS_PrepareMeasure.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(MeasConfigType),
        ]
        dll.AVS_PrepareMeasure.restype = ctypes.c_int

        # int AVS_Measure(AvsHandle, callback, short Nmsr)  — versão callback
        MEAS_CB = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int))
        dll.AVS_MeasureCallback.argtypes = [ctypes.c_long, MEAS_CB, ctypes.c_short]
        dll.AVS_MeasureCallback.restype  = ctypes.c_int
        self._MEAS_CB = MEAS_CB   # mantém referência viva

        # int AVS_Measure(AvsHandle, void* hWnd, short Nmsr) — versão polling (hWnd=NULL)
        dll.AVS_Measure.argtypes = [ctypes.c_long, ctypes.c_void_p, ctypes.c_short]
        dll.AVS_Measure.restype  = ctypes.c_int

        # int AVS_PollScan(AvsHandle)
        dll.AVS_PollScan.argtypes = [ctypes.c_long]
        dll.AVS_PollScan.restype  = ctypes.c_int

        # int AVS_GetScopeData(AvsHandle, uint* a_pTimeLabel, double* a_pSpectrum)
        dll.AVS_GetScopeData.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_double),
        ]
        dll.AVS_GetScopeData.restype = ctypes.c_int

        # int AVS_StopMeasure(AvsHandle)
        dll.AVS_StopMeasure.argtypes = [ctypes.c_long]
        dll.AVS_StopMeasure.restype  = ctypes.c_int

        # int AVS_GetLambda(AvsHandle, double* a_pWaveLength)
        dll.AVS_GetLambda.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_double),
        ]
        dll.AVS_GetLambda.restype = ctypes.c_int

        # int AVS_GetNumPixels(AvsHandle, unsigned short* a_pNumPixels)
        dll.AVS_GetNumPixels.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_ushort),
        ]
        dll.AVS_GetNumPixels.restype = ctypes.c_int

        # int AVS_GetParameter(AvsHandle, uint, uint*, DeviceConfigType*)
        dll.AVS_GetParameter.argtypes = [
            ctypes.c_long,
            ctypes.c_uint,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(DeviceConfigType),
        ]
        dll.AVS_GetParameter.restype = ctypes.c_int

        # int AVS_SetParameter(AvsHandle, DeviceConfigType*)
        dll.AVS_SetParameter.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(DeviceConfigType),
        ]
        dll.AVS_SetParameter.restype = ctypes.c_int

        # int AVS_GetVersionInfo(AvsHandle, char*, char*, char*)
        dll.AVS_GetVersionInfo.argtypes = [
            ctypes.c_long,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        dll.AVS_GetVersionInfo.restype = ctypes.c_int

        # int AVS_GetDLLVersion(char*)
        dll.AVS_GetDLLVersion.argtypes = [ctypes.c_char_p]
        dll.AVS_GetDLLVersion.restype  = ctypes.c_int

        # int AVS_GetDarkPixelData(AvsHandle, double*)
        dll.AVS_GetDarkPixelData.argtypes = [
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_double),
        ]
        dll.AVS_GetDarkPixelData.restype = ctypes.c_int

        # int AVS_SetPrescanMode(AvsHandle, bool)   ← específico para 3648!
        dll.AVS_SetPrescanMode.argtypes = [ctypes.c_long, ctypes.c_bool]
        dll.AVS_SetPrescanMode.restype  = ctypes.c_int

        # int AVS_UseHighResAdc(AvsHandle, bool)
        dll.AVS_UseHighResAdc.argtypes = [ctypes.c_long, ctypes.c_bool]
        dll.AVS_UseHighResAdc.restype  = ctypes.c_int

        # int AVS_GetDetectorName(AvsHandle, uint8, char*)
        dll.AVS_GetDetectorName.argtypes = [
            ctypes.c_long,
            ctypes.c_uint8,
            ctypes.c_char_p,
        ]
        dll.AVS_GetDetectorName.restype = ctypes.c_int

        print("   Protótipos configurados ✔")

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def init(self, port: int = 0) -> int:
        """
        Inicializa a comunicação com o espectrômetro.

        port: 0 = USB (padrão), -1 = USB + Ethernet, 256 = Ethernet
        Retorna o número de dispositivos encontrados.
        """
        self._load_dll()
        n = self._dll.AVS_Init(ctypes.c_short(port))
        if n < 0:
            raise RuntimeError(f"AVS_Init falhou: {avs_error_str(n)}")
        print(f"🔌 AVS_Init OK — {n} dispositivo(s) encontrado(s)")
        return n

    def close(self):
        """Desativa o dispositivo e libera a DLL."""
        if self._handle is not None:
            self._dll.AVS_Deactivate(self._handle)
            self._handle = None
        if self._dll:
            self._dll.AVS_Done()
            self._dll = None
        print("  Conexão encerrada.")

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *_):
        self.close()

    # ------------------------------------------------------------------
    # Descoberta e seleção de dispositivos
    # ------------------------------------------------------------------

    def get_device_list(self) -> List[AvsIdentityType]:
        """
        Escaneia e retorna a lista de espectrômetros conectados.
        """
        n = self._dll.AVS_UpdateUSBDevices()
        if n <= 0:
            raise RuntimeError("Nenhum dispositivo USB detectado.")

        required = ctypes.c_uint(0)
        # Primeira chamada para saber o tamanho necessário
        self._dll.AVS_GetList(0, ctypes.byref(required), None)

        n_devs = required.value // ctypes.sizeof(AvsIdentityType)
        arr    = (AvsIdentityType * n_devs)()
        count  = self._dll.AVS_GetList(
            required.value,
            ctypes.byref(required),
            arr,
        )
        if count < 0:
            raise RuntimeError(f"AVS_GetList falhou: {avs_error_str(count)}")

        self._devices = list(arr[:count])
        print(f"\n  Dispositivos encontrados: {count}")
        for i, d in enumerate(self._devices):
            print(f"   [{i}] Serial: {d.SerialNumber.decode()!r:12s} "
                  f"| Nome: {d.UserFriendlyName.decode()!r:20s} "
                  f"| Status: {d.Status}")
        return self._devices

    def activate(self, device_index: int = 0, dbg: bool = True) -> int:
        """
        Ativa o espectrômetro pelo índice na lista de dispositivos.
        Retorna o handle (inteiro) para uso em chamadas subsequentes.
        """
        if not self._devices:
            self.get_device_list()

        dev    = self._devices[device_index]
        handle = self._dll.AVS_Activate(ctypes.byref(dev))

        if handle == INVALID_AVS_HANDLE_VALUE or handle <= 0:
            raise RuntimeError(
                f"AVS_Activate falhou para o dispositivo {device_index}. "
                f"handle={handle}"
            )
        self._handle = handle
        if dbg is True:
            print(f"Dispositivo {device_index} ativado — handle={handle}")

        # Lê número de pixels do sensor
        n_pix = ctypes.c_ushort(0)
        ret   = self._dll.AVS_GetNumPixels(self._handle, ctypes.byref(n_pix))
        self._check(ret, "AVS_GetNumPixels")
        self._n_pixels = n_pix.value
        if dbg is True:
            print(f"   Pixels: {self._n_pixels}")

        return handle

    # ------------------------------------------------------------------
    # Informações sobre versão e detector
    # ------------------------------------------------------------------

    def get_dll_version(self) -> str:
        buf = ctypes.create_string_buffer(VERSION_LEN)
        self._dll.AVS_GetDLLVersion(buf)
        return buf.value.decode()

    def get_version_info(self) -> Tuple[str, str, str]:
        """Retorna (fpga_version, firmware_version, dll_version)."""
        fpga = ctypes.create_string_buffer(VERSION_LEN)
        firm = ctypes.create_string_buffer(VERSION_LEN)
        dll  = ctypes.create_string_buffer(VERSION_LEN)
        ret  = self._dll.AVS_GetVersionInfo(self._handle, fpga, firm, dll)
        self._check(ret, "AVS_GetVersionInfo")
        return fpga.value.decode(), firm.value.decode(), dll.value.decode()

    def get_detector_name(self) -> str:
        buf = ctypes.create_string_buffer(DETECTOR_NAME_LEN)
        ret = self._dll.AVS_GetDetectorName(self._handle, 0, buf)
        self._check(ret, "AVS_GetDetectorName")
        return buf.value.decode()

    def print_info(self):
        """Imprime resumo das informações do dispositivo."""
        fpga, firm, dll = self.get_version_info()
        det = self.get_detector_name()
        print("\n  Informações do espectrômetro:")
        print(f"   FPGA     : {fpga}")
        print(f"   Firmware : {firm}")
        print(f"   DLL      : {dll}")
        print(f"   Detector : {det}")
        print(f"   Pixels   : {self._n_pixels}")

    # ------------------------------------------------------------------
    # Configuração da medição
    # ------------------------------------------------------------------

    def configure(
        self,
        integration_time_ms: float  = 10.0,
        nr_averages:         int    = 1,
        start_pixel:         int    = 0,
        stop_pixel:          Optional[int] = None,
        trigger_mode:        int    = SW_TRIGGER_MODE,
        dynamic_dark:        bool   = False,
        smooth_pixels:       int    = 0,
        saturation_detect:   bool   = True,
        prescan_mode:        bool   = True,
        high_res_adc:        bool   = True,
        dbg:                 bool   = True
    ):
        """
        Configura os parâmetros de medição e envia para o espectrômetro.

        integration_time_ms : tempo de integração em milissegundos (mín ~1,1 ms para TCD)
        nr_averages         : número de médias (1 = sem média)
        start_pixel         : pixel inicial do range (0-based)
        stop_pixel          : pixel final (None = último pixel)
        trigger_mode        : 0=SW, 1=HW, 2=Sync-Start
        dynamic_dark        : habilita correção dinâmica de dark
        smooth_pixels       : janela de suavização em pixels (0 = sem suavização)
        saturation_detect   : detecta pixels saturados
        prescan_mode        : True = Prescan (padrão 3648), False = Clear mode
        high_res_adc        : True = 16-bit ADC (hardware ≥ v3)
        """
        if self._handle is None:
            raise RuntimeError("Dispositivo não ativado. Chame activate() primeiro.")

        if stop_pixel is None:
            stop_pixel = self._n_pixels - 1

        if integration_time_ms < MIN_ILX_INTTIME:
            print(f"⚠️  Tempo de integração {integration_time_ms} ms < mínimo "
                  f"({MIN_ILX_INTTIME} ms). Ajustando.")
            integration_time_ms = MIN_ILX_INTTIME

        cfg = MeasConfigType()
        cfg.m_StartPixel                     = start_pixel
        cfg.m_StopPixel                      = stop_pixel
        cfg.m_IntegrationTime                = integration_time_ms
        cfg.m_IntegrationDelay               = 0
        cfg.m_NrAverages                     = nr_averages
        cfg.m_CorDynDark.m_Enable            = 1 if dynamic_dark else 0
        cfg.m_CorDynDark.m_ForgetPercentage  = 100
        cfg.m_Smoothing.m_SmoothPix          = smooth_pixels
        cfg.m_Smoothing.m_SmoothModel        = 0
        cfg.m_SaturationDetection            = 1 if saturation_detect else 0
        cfg.m_Trigger.m_Mode                 = trigger_mode
        cfg.m_Trigger.m_Source               = EXTERNAL_TRIGGER
        cfg.m_Trigger.m_SourceType           = EDGE_TRIGGER_SOURCE
        cfg.m_Control.m_StrobeControl        = 0
        cfg.m_Control.m_LaserDelay           = 0
        cfg.m_Control.m_LaserWidth           = 0
        cfg.m_Control.m_LaserWaveLength      = 0.0
        cfg.m_Control.m_StoreToRam           = 0
        self._meas_cfg = cfg

        # Modo prescan (específico AvaSpec-3648 — sensor TCD1304)
        ret = self._dll.AVS_SetPrescanMode(self._handle, prescan_mode)
        self._check(ret, "AVS_SetPrescanMode")

        # ADC de alta resolução
        ret = self._dll.AVS_UseHighResAdc(self._handle, high_res_adc)
        self._check(ret, "AVS_UseHighResAdc")

        # Envia configuração para o hardware
        ret = self._dll.AVS_PrepareMeasure(self._handle, ctypes.byref(cfg))
        self._check(ret, "AVS_PrepareMeasure")

        if dbg is True:
            print(f"\n   Configuração aplicada:")
            print(f"   Tempo de integração : {integration_time_ms:.2f} ms")
            print(f"   Médias              : {nr_averages}")
            print(f"   Pixels              : [{start_pixel}, {stop_pixel}]")
            print(f"   Trigger             : {['SW', 'HW', 'Sync'][trigger_mode]}")
            print(f"   Prescan (TCD3648)   : {prescan_mode}")
            print(f"   ADC 16-bit          : {high_res_adc}")


    # Comprimentos de onda (calibração de fábrica)


    def get_wavelengths(self) -> List[float]:
        """
        Retorna o array de comprimentos de onda [nm] para cada pixel,
        calculado a partir dos coeficientes de calibração gravados no
        espectrômetro (polinômio de 5º grau, fit do fabricante).
        """
        buf = (ctypes.c_double * self._n_pixels)()
        ret = self._dll.AVS_GetLambda(self._handle, buf)
        self._check(ret, "AVS_GetLambda")
        return list(buf)


    # Aquisição de espectro


    def measure_single(
        self,
        integration_time_ms: Optional[float] = None,
        nr_averages: Optional[int] = None,
        timeout_s: float = 10.0,
    ) -> Tuple[List[float], List[float]]:
        """
        Realiza uma medição simples e retorna (wavelengths, spectrum).

        Se integration_time_ms ou nr_averages forem fornecidos, reconfigura
        antes de medir. Caso contrário usa os parâmetros já configurados.

        Retorna:
            wavelengths : lista de floats com os comprimentos de onda [nm]
            spectrum    : lista de floats com as contagens por pixel
        """
        if integration_time_ms is not None or nr_averages is not None:
            cfg_kwargs = {}
            if integration_time_ms is not None:
                cfg_kwargs["integration_time_ms"] = integration_time_ms
            if nr_averages is not None:
                cfg_kwargs["nr_averages"] = nr_averages
            self.configure(**cfg_kwargs)

        # Dispara 1 medição via polling puro:
        # AVS_Measure com hWnd=NULL → sem notificação de janela Windows,
        # resultado verificado manualmente com AVS_PollScan
        ret = self._dll.AVS_Measure(
            self._handle,
            None,   # hWnd = NULL → modo polling
            1,      # Nmsr = 1 medição
        )
        self._check(ret, "AVS_Measure")

        # Polling até os dados ficarem prontos
        t0 = time.time()
        while True:
            ready = self._dll.AVS_PollScan(self._handle)
            if ready == 1:
                break
            if ready < 0:
                raise RuntimeError(f"AVS_PollScan erro: {avs_error_str(ready)}")
            if time.time() - t0 > timeout_s:
                self._dll.AVS_StopMeasure(self._handle)
                raise TimeoutError(
                    f"Timeout após {timeout_s}s aguardando dados do espectrômetro."
                )
            time.sleep(0.001)

        # Recupera os dados
        time_label = ctypes.c_uint(0)
        spectrum   = (ctypes.c_double * self._n_pixels)()
        ret = self._dll.AVS_GetScopeData(
            self._handle,
            ctypes.byref(time_label),
            spectrum,
        )
        self._check(ret, "AVS_GetScopeData")

        wavelengths = self.get_wavelengths()
        return wavelengths, list(spectrum)

    def measure_average(
        self,
        n_scans: int = 5,
        integration_time_ms: Optional[float] = None,
    ) -> Tuple[List[float], List[float]]:
        """
        Realiza n_scans medições e retorna a média dos espectros.
        Útil para reduzir ruído sem usar a média interna do hardware.
        """
        spectra = []
        for i in range(n_scans):
            wl, sp = self.measure_single(integration_time_ms=integration_time_ms
                                         if i == 0 else None)
            spectra.append(sp)

        n_pix = len(spectra[0])
        avg   = [sum(spectra[j][k] for j in range(n_scans)) / n_scans
                 for k in range(n_pix)]
        return wl, avg

    def get_dark_pixels(self) -> List[float]:
        """
        Retorna os pixels escuros ópticos (optical black) da última medição.
        Para o AvaSpec-3648 (TCD1304): 13 pixels dark.
        Deve ser chamado APÓS AVS_GetScopeData.
        """
        # TCD: 13 dark pixels
        buf = (ctypes.c_double * TCD_TOTAL_DARK_PIXELS)()
        ret = self._dll.AVS_GetDarkPixelData(self._handle, buf)
        if ret != 1:
            raise RuntimeError(f"AVS_GetDarkPixelData falhou: {avs_error_str(ret)}")
        return list(buf)

    # ------------------------------------------------------------------
    # Parâmetros avançados do dispositivo
    # ------------------------------------------------------------------

    def get_device_config(self) -> DeviceConfigType:
        """Lê a estrutura completa de configuração do espectrômetro."""
        required = ctypes.c_uint(0)
        cfg      = DeviceConfigType()
        ret = self._dll.AVS_GetParameter(
            self._handle,
            ctypes.sizeof(DeviceConfigType),
            ctypes.byref(required),
            ctypes.byref(cfg),
        )
        self._check(ret, "AVS_GetParameter")
        return cfg

    def print_device_config(self):
        """Imprime os campos mais relevantes da configuração do dispositivo."""
        cfg = self.get_device_config()
        det = cfg.m_Detector
        print("\n  Configuração do Dispositivo:")
        print(f"   Config version   : {cfg.m_ConfigVersion}")
        print(f"   User ID          : {cfg.m_aUserFriendlyId.decode()!r}")
        print(f"   Sensor type      : {det.m_SensorType}")
        print(f"   Nr pixels        : {det.m_NrPixels}")
        print(f"   Wavelength coefs : {list(det.m_aFit)}")
        print(f"   Gain ch0         : {det.m_Gain[0]:.4f}")
        print(f"   Gain ch1         : {det.m_Gain[1]:.4f}")
        print(f"   Offset ch0       : {det.m_Offset[0]:.4f}")
        print(f"   NL correction    : {'ativo' if det.m_NLEnable else 'inativo'}")

    # ------------------------------------------------------------------
    # Utilitários internos
    # ------------------------------------------------------------------

    def _check(self, ret: int, fn_name: str):
        if ret != ERR_SUCCESS:
            raise RuntimeError(f"{fn_name} falhou: {avs_error_str(ret)} (código {ret})")

    @property
    def n_pixels(self) -> int:
        return self._n_pixels

    @property
    def handle(self):
        return self._handle


# ---------------------------------------------------------------------------
# Exemplo de uso completo
# ---------------------------------------------------------------------------

def exemplo_completo():
    """
    Demonstração do fluxo completo de aquisição com o AvaSpec-3648.
    """
    DLL_PATH = dll_path

    # Versão da DLL antes de inicializar
    try:
        _dll_tmp = ctypes.WinDLL(DLL_PATH)
        _dll_tmp.AVS_GetDLLVersion.argtypes = [ctypes.c_char_p]
        _dll_tmp.AVS_GetDLLVersion.restype  = ctypes.c_int
        _vbuf = ctypes.create_string_buffer(VERSION_LEN)
        _dll_tmp.AVS_GetDLLVersion(_vbuf)
        print(f"\n  DLL Version: {_vbuf.value.decode()}")
    except Exception:
        pass

    spec = AvaSpec(DLL_PATH)

    try:
        # 1. Inicializar comunicação
        n = spec.init(port=0)  # USB

        # 2. Listar dispositivos
        devices = spec.get_device_list()

        # 3. Ativar o primeiro dispositivo
        spec.activate(0)

        # 4. Informações de versão
        spec.print_info()

        # 5. Configuração do espectrômetro
        spec.configure(
            integration_time_ms = 1000.0,
            nr_averages          = 1,
            prescan_mode         = True,   # recomendado para AvaSpec-3648
            high_res_adc         = True,   # 16-bit ADC
            saturation_detect    = True,
        )

        # 6. Medição simples
        print("\n  Iniciando medição...")
        wavelengths, spectrum = spec.measure_single()

        print(f"\n   Comprimento de onda range: "
              f"{wavelengths[0]:.2f} - {wavelengths[-1]:.2f} nm")
        print(f"   Pico máximo: {max(spectrum):.1f} counts "
              f"@ pixel {spectrum.index(max(spectrum))}")
        print(f"   Pico mínimo: {min(spectrum):.1f} counts")

        # 7. Pixels dark (TCD1304 → 13 pixels)
        try:
            dark = spec.get_dark_pixels()
            print(f"\n   Dark pixels (TCD): {[f'{v:.1f}' for v in dark]}")
        except Exception as e:
            print(f"   Dark pixels: {e}")

        # 8. Configuração completa do dispositivo
        spec.print_device_config()

        # 9. Exemplo de medição com média manual (5 scans)
        print("\n  Medição com média (5 scans)...")
        wl_avg, sp_avg = spec.measure_average(n_scans=5)
        print(f"   Média do pico máximo: {max(sp_avg):.2f} counts")

        # 10. Salva resultado em CSV simples
        csv_path = "espectro_avaspec3648.csv"
        with open(csv_path, "w") as f:
            f.write("wavelength_nm,intensity_counts\n")
            for wl, val in zip(wavelengths, spectrum):
                f.write(f"{wl:.6f},{val:.6f}\n")
        print(f"\n  Espectro salvo em: {csv_path}")

    except Exception as e:
        print(f"\n  Erro: {e}")
        raise

    finally:
        spec.close()


if __name__ == "__main__":
    # Verifica que está rodando em Windows (necessário para a DLL)
    if sys.platform != "win32":
        print(" !!!  Este driver requer Windows com a avaspecx64.dll instalada.")
        print("   Em Linux/Mac, use a libavs.so (não incluída aqui).")
        sys.exit(1)

    exemplo_completo()

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, Union

# All of the containers would probably be better of using dacite, but since HA sometimes has issues with dacite I am
# doing them manually


@dataclass
class APCUpdateBinary:
    cooking: bool
    preheating: bool | None = None
    maintaining: bool | None = None
    device_safe: bool | None = None
    water_leak: bool | None = None
    water_level_critical: bool | None = None
    water_temp_too_high: bool | None = None
    water_level_low: bool | None = None


@dataclass
class APCUpdateSensor:
    cook_time: int | None = None
    mode: str | None = None
    state: str | None = None
    a3_state: str | None = None
    target_temperature: float | None = None
    cook_time_remaining: int | None = None
    firmware_version: str | None = None
    heater_temperature: float | None = None
    triac_temperature: float | None = None
    water_temperature: float | None = None
    current_temperature: float | None = None


@dataclass
class APCUpdate:
    binary_sensor: APCUpdateBinary
    sensor: APCUpdateSensor


class AnovaMode(str, Enum):
    startup = "STARTUP"
    idle = "IDLE"
    cook = "COOK"
    low_water = "LOW WATER"
    ota = "OTA"
    provisioning = "PROVISIONING"
    high_temp = "HIGH TEMP"
    device_failure = "DEVICE FAILURE"


class AnovaState(str, Enum):
    preheating = "PREHEATING"
    cooking = "COOKING"
    maintaining = "MAINTAINING"
    timer_expired = "TIMER EXPIRED"
    set_timer = "SET TIMER"
    no_state = ""


class AnovaA3State(str, Enum):
    no_state = "none"
    connected = "connected"
    disconnected = "disconnected"
    heating = "heating"
    keeping_warm = "keeping_warm"
    cooking = "cooking"
    reconnecting = "reconnecting"


class AnovaCommand(str, Enum):
    EVENT_APC_WIFI_LIST = "EVENT_APC_WIFI_LIST"
    EVENT_APC_STATE = "EVENT_APC_STATE"
    EVENT_APC_WIFI_VERSION = "EVENT_APC_WIFI_VERSION"
    EVENT_APC_WIFI_ADDED = "EVENT_APC_WIFI_ADDED"
    EVENT_APC_WIFI_REMOVED = "EVENT_APC_WIFI_REMOVED"
    CMD_APC_SET_TARGET_TEMP = "CMD_APC_SET_TARGET_TEMP"
    CMD_APC_SET_TIMER = "CMD_APC_SET_TIMER"
    CMD_APC_START = "CMD_APC_START"
    CMD_APC_STOP = "CMD_APC_STOP"
    RESPONSE = "RESPONSE"

    # Grabbed from apk
    CMD_AUTH_TOKEN = "CMD_AUTH_TOKEN"
    AUTH_TOKEN_V2 = "AUTH_TOKEN_V2"
    CMD_APC_SET_METADATA = "CMD_APC_SET_METADATA"
    CMD_APC_SET_TEMPERATURE_UNIT = "CMD_APC_SET_TEMPERATURE_UNIT"
    CMD_APC_OTA = "CMD_APC_OTA"
    CMD_NAME_WIFI_DEVICE = "CMD_NAME_WIFI_DEVICE"
    CMD_APC_A3_SET_CREDENTIALS = "CMD_APC_A3_SET_CREDENTIALS"
    CMD_APC_REGISTER_PUSH_TOKEN = "CMD_APC_REGISTER_PUSH_TOKEN"
    CMD_APC_START_ICEBATH_MONITORING = "CMD_APC_START_ICEBATH_MONITORING"
    CMD_APC_DISCONNECT = "CMD_APC_DISCONNECT"
    CMD_APC_HEALTHCHECK = "CMD_APC_HEALTHCHECK"

    # Oven specific commands
    CMD_OVEN_SET_MODE = "CMD_OVEN_SET_MODE"
    CMD_OVEN_SET_TEMP = "CMD_OVEN_SET_TEMP"
    CMD_OVEN_SET_STEAM = "CMD_OVEN_SET_STEAM"
    CMD_OVEN_SET_TIMER = "CMD_OVEN_SET_TIMER"
    CMD_OVEN_START = "CMD_OVEN_START"
    CMD_OVEN_STOP = "CMD_OVEN_STOP"
    CMD_OVEN_LIGHT = "CMD_OVEN_LIGHT"

    # New commands for the Anova Precision Oven
    EVENT_APO_STATE = "EVENT_APO_STATE"
    EVENT_APO_WIFI_LIST = "EVENT_APO_WIFI_LIST"
    EVENT_APO_WIFI_VERSION = "EVENT_APO_WIFI_VERSION"
    EVENT_APO_WIFI_ADDED = "EVENT_APO_WIFI_ADDED"
    EVENT_APO_WIFI_REMOVED = "EVENT_APO_WIFI_REMOVED"
    CMD_APO_SET_MODE = "CMD_APO_SET_MODE"
    CMD_APO_SET_TEMP = "CMD_APO_SET_TEMP"
    CMD_APO_SET_STEAM = "CMD_APO_SET_STEAM"
    CMD_APO_SET_TIMER = "CMD_APO_SET_TIMER"
    CMD_APO_START = "CMD_APO_START"
    CMD_APO_STOP = "CMD_APO_STOP"
    CMD_APO_LIGHT = "CMD_APO_LIGHT"


@dataclass
class WifiJob:
    id: str
    cook_time_seconds: int
    target_temperature: float
    temperature_unit: str
    mode: AnovaMode
    ota_url: str


@dataclass
class WifiJobStatus:
    cook_time_remaining: int | None
    state: AnovaState


@dataclass
class WifiPinInfo:
    is_device_safe: bool | None
    is_water_leak: bool | None
    is_water_level_critical: bool | None
    is_water_level_low: bool | None
    water_temp_too_high: bool | None


@dataclass
class WifiSystemInfo:
    firmware_version: str
    class_name: str | None = None
    type: str | None = None


@dataclass
class WifiSystemInfo3220:
    firmware_version: str
    has_real_cert_catalog: str | None = None
    firmware_version_raw: str | None = None
    largest_free_heap_size: int | None = None
    stack_low_level: int | None = None
    stack_low_task: int | None = None
    systick: int | None = None
    total_free_heap_size: int | None = None


@dataclass
class WifiSystemInfoNxp:
    firmware_version: str  # 'version-string'


@dataclass
class WifiTemperatureInfo:
    """Gets temperature info for the device. All in celsius."""

    heater_temperature: float | None
    triac_temperature: float | None
    water_temperature: float


@dataclass
class WifiCookerStateBody:
    audio_control: Any | None
    boot_id: str | None
    cap_touch: Any | None
    heater_control: Any | None
    job: WifiJob
    job_status: WifiJobStatus
    motor_control: Any | None
    network_info: Any | None
    pin_info: WifiPinInfo
    system_info: WifiSystemInfo | None
    system_info_3220: WifiSystemInfo3220 | None
    system_info_nxp: WifiSystemInfoNxp | None
    temperature_info: WifiTemperatureInfo

    @property
    def firmware_version(self) -> str:
        if self.system_info:
            return self.system_info.firmware_version
        if self.system_info_3220:
            return self.system_info_3220.firmware_version
        if self.system_info_nxp:
            return self.system_info_nxp.firmware_version
        else:
            return "unknown"

    def to_apc_update(self) -> APCUpdate:
        sensors = APCUpdateSensor(
            cook_time=self.job.cook_time_seconds,
            mode=self.job.mode.name,
            state=self.job_status.state.name,
            target_temperature=self.job.target_temperature,
            cook_time_remaining=self.job_status.cook_time_remaining,
            firmware_version=self.firmware_version,
            heater_temperature=self.temperature_info.heater_temperature,
            triac_temperature=self.temperature_info.triac_temperature,
            water_temperature=self.temperature_info.water_temperature,
        )

        binary_sensors = APCUpdateBinary(
            cooking=bool(self.job.mode == AnovaMode.cook),
            preheating=bool(self.job_status.state == AnovaState.preheating),
            maintaining=bool(
                self.job_status.state == AnovaState.maintaining
                or self.job_status.state == AnovaState.timer_expired
            ),
            device_safe=self.pin_info.is_device_safe,
            water_leak=self.pin_info.is_water_leak,
            water_level_critical=self.pin_info.is_water_level_critical,
            water_temp_too_high=self.pin_info.water_temp_too_high,
            water_level_low=self.pin_info.is_water_level_low,
        )
        return APCUpdate(sensor=sensors, binary_sensor=binary_sensors)


def build_wifi_cooker_state_body(apc_response: dict[str, Any]) -> WifiCookerStateBody:
    system_info = None
    system_info_3220 = None
    system_info_nxp = None
    audio_control = apc_response.get("audio-control")
    boot_id = apc_response.get("boot-id")
    cap_touch = apc_response.get("cap-touch")
    heater_control = apc_response.get("heater-control")
    job_json: dict[str, Any] = apc_response["job"]
    job = WifiJob(
        id=job_json["id"],
        cook_time_seconds=job_json["cook-time-seconds"],
        mode=AnovaMode(job_json["mode"]),
        ota_url=job_json["ota-url"],
        target_temperature=job_json["target-temperature"],
        temperature_unit=job_json["temperature-unit"],
    )
    job_status_json: dict[str, Any] = apc_response["job-status"]
    job_status = WifiJobStatus(
        cook_time_remaining=job_status_json.get("cook-time-remaining"),
        state=AnovaState(job_status_json["state"]),
    )
    network_info = apc_response.get("network-info")
    motor_control = apc_response.get("motor-control")
    pin_info_json: dict[str, int] = apc_response["pin-info"]
    pin_info = WifiPinInfo(
        is_device_safe=bool(pin_info_json["device-safe"])
        if "device-safe" in pin_info_json
        else None,
        is_water_leak=bool(pin_info_json.get("water-leak"))
        if "water-leak" in pin_info_json
        else None,
        is_water_level_critical=bool(pin_info_json.get("water-level-critical"))
        if "water-level-critical" in pin_info_json
        else None,
        is_water_level_low=bool(pin_info_json.get("water-level-low"))
        if "water-level-low" in pin_info_json
        else None,
        water_temp_too_high=bool(pin_info_json.get("water-temp-too-high"))
        if "water-temp-too-high" in pin_info_json
        else None,
    )
    system_info_json: dict[str, str] | None = apc_response.get("system-info")
    if system_info_json is not None:
        system_info = WifiSystemInfo(
            firmware_version=system_info_json["firmware-version"],
            class_name=system_info_json.get("class"),
            type=system_info_json.get("type"),
        )
    system_info_3220_json: dict[str, str] | None = apc_response.get("system-info-3220")
    if system_info_3220_json:
        largest_free_heap_size = system_info_3220_json.get("largest-free-heap-size")
        system_info_3220 = WifiSystemInfo3220(
            firmware_version=system_info_3220_json["firmware-version"],
            has_real_cert_catalog=system_info_3220_json.get("has-real-cert-catalog"),
            firmware_version_raw=system_info_3220_json.get("firmware-version-raw"),
            largest_free_heap_size=int(largest_free_heap_size)
            if largest_free_heap_size is not None
            else None,
            # Too lazy to do these right now.
            # stack_low_level=system_info_3220_json.get("stack-low-level"),
            # stack_low_task=system_info_3220_json.get("stack-low-task"),
            # systick=system_info_3220_json.get("systick"),
            # total_free_heap_size=system_info_3220_json.get("total-free-heap-size"),
        )
    system_info_nxp_json: dict[str, str] | None = apc_response.get("system-info-nxp")
    if system_info_nxp_json:
        system_info_nxp = WifiSystemInfoNxp(
            firmware_version=system_info_nxp_json["version-string"]
        )
    temperature_info_json: dict[str, float] = apc_response["temperature-info"]
    temperature_info = WifiTemperatureInfo(
        heater_temperature=temperature_info_json.get("heater-temperature"),
        water_temperature=temperature_info_json["water-temperature"],
        triac_temperature=temperature_info_json.get("triac-temperature"),
    )
    return WifiCookerStateBody(
        audio_control=audio_control,
        boot_id=boot_id,
        cap_touch=cap_touch,
        heater_control=heater_control,
        job=job,
        job_status=job_status,
        motor_control=motor_control,
        pin_info=pin_info,
        system_info=system_info,
        system_info_3220=system_info_3220,
        system_info_nxp=system_info_nxp,
        temperature_info=temperature_info,
        network_info=network_info,
    )


def build_a3_payload(apc_response: dict[str, Any]) -> APCUpdate:
    firmware_version: str = apc_response["firmwareVersion"]
    is_cooking: bool = apc_response["isCooking"]
    current_temperature: float = apc_response["currentTemperature"]
    target_temperature: float = apc_response["targetTemperature"]
    timer_in_seconds: int = apc_response["timerInSeconds"]
    # unit = apc_response.get("unit")
    # is_timer_running = apc_response.get("isTimerRunning")
    # is_speaker_on = apc_response.get("isSpeakerOn")
    # is_alarm_active = apc_response.get("isAlarmActive")
    # current_job_id = apc_response.get("currentJobID")
    current_job = apc_response.get("currentJob")
    # is_keeping_warm = apc_response.get("isKeepingWarming")
    # is_checking_temperature_for_ice_bath = apc_response.get(
    #     "isCheckingTemperatureForIceBath"
    # )
    # is_monitoring_ice_bath = apc_response.get("isMonitoringIcebath")
    # is_connected = apc_response.get("isConnected")
    if current_job is not None:
        job_stage: str = current_job["jobStage"]
        status = AnovaA3State(job_stage)
    else:
        status = AnovaA3State.no_state
    sensors = APCUpdateSensor(
        a3_state=status.name,
        target_temperature=float(target_temperature),
        cook_time_remaining=int(timer_in_seconds),
        firmware_version=firmware_version,
        water_temperature=float(current_temperature),
    )

    binary_sensors = APCUpdateBinary(
        cooking=bool(is_cooking),
        preheating=bool(status == AnovaState.preheating),
        maintaining=bool(
            status == AnovaState.maintaining or status == AnovaState.timer_expired
        ),
    )
    return APCUpdate(binary_sensors, sensors)


def build_a6_a7_payload(apc_response: dict[str, Any]) -> APCUpdate:
    system_info = apc_response["systemInfo"]
    firmware_version = system_info["firmwareVersion"]
    mode = apc_response["state"]["mode"]
    nodes = apc_response["nodes"]
    sensors = APCUpdateSensor(
        firmware_version=firmware_version,
        mode=mode,
        water_temperature=float(nodes["waterTemperatureSensor"]["current"]["celsius"]),
        target_temperature=float(
            nodes["waterTemperatureSensor"]["setpoint"]["celsius"]
        ),
        cook_time=int(nodes["timer"]["initial"]),
    )
    binary_sensors = APCUpdateBinary(
        cooking=bool(mode == "cook"),
        water_level_low=bool(nodes["lowWater"]["warning"]),
        water_level_critical=bool(nodes["lowWater"]["empty"]),
    )
    return APCUpdate(binary_sensors, sensors)


class OvenMode(str, Enum):
    STANDBY = "standby"
    COOKING = "cooking"
    PREHEATING = "preheating"
    COOLING = "cooling"
    ERROR = "error"


class OvenStage(str, Enum):
    STEAM = "steam"
    SOUS_VIDE = "sous_vide"
    DRY = "dry"
    PROOF = "proof"


@dataclass
class OvenStateBody:
    mode: OvenMode
    stage: Optional[OvenStage]
    target_temperature: float
    current_temperature: float
    target_steam: Optional[int]
    current_steam: Optional[int]
    timer_remaining: Optional[int]
    door_open: bool
    light_on: bool
    error_code: Optional[str]


@dataclass
class OvenUpdateSensor:
    mode: str
    stage: Optional[str]
    target_temperature: float
    current_temperature: float
    target_steam: Optional[int]
    current_steam: Optional[int]
    timer_remaining: Optional[int]

    @classmethod
    def from_state(cls, state: OvenStateBody) -> "OvenUpdateSensor":
        return cls(
            mode=state.mode.value,
            stage=state.stage.value if state.stage else None,
            target_temperature=state.target_temperature,
            current_temperature=state.current_temperature,
            target_steam=state.target_steam,
            current_steam=state.current_steam,
            timer_remaining=state.timer_remaining,
        )


@dataclass
class OvenUpdateBinary:
    cooking: bool
    preheating: bool
    door_open: bool
    light_on: bool
    error: bool

    @classmethod
    def from_state(cls, state: OvenStateBody) -> "OvenUpdateBinary":
        return cls(
            cooking=state.mode == OvenMode.COOKING,
            preheating=state.mode == OvenMode.PREHEATING,
            door_open=state.door_open,
            light_on=state.light_on,
            error=bool(state.error_code) or state.mode == OvenMode.ERROR,
        )


@dataclass
class OvenUpdate:
    binary_sensor: OvenUpdateBinary
    sensor: OvenUpdateSensor

    @classmethod
    def from_state(cls, state: OvenStateBody) -> "OvenUpdate":
        return cls(
            sensor=OvenUpdateSensor.from_state(state),
            binary_sensor=OvenUpdateBinary.from_state(state),
        )


def build_oven_state_body(state_data: dict[str, Any]) -> OvenStateBody:
    """Build an oven state body from raw state data."""
    return OvenStateBody(
        mode=OvenMode(state_data.get("mode", "standby")),
        stage=OvenStage(state_data["stage"]) if "stage" in state_data else None,
        target_temperature=float(state_data.get("target_temp", 0)),
        current_temperature=float(state_data.get("current_temp", 0)),
        target_steam=state_data.get("target_steam"),
        current_steam=state_data.get("current_steam"),
        timer_remaining=state_data.get("timer"),
        door_open=bool(state_data.get("door_open", False)),
        light_on=bool(state_data.get("light", False)),
        error_code=state_data.get("error_code"),
    )


@dataclass
class APCWifiDevice:
    id: str
    name: str
    state: dict[str, Any]
    device_type: str = "sous_vide"
    update_listener: Optional[Callable[[Union[APCUpdate, OvenUpdate]], None]] = None

    def to_update(self) -> Union[APCUpdate, OvenUpdate]:
        """Convert device state to update object based on device type."""
        if self.device_type == "oven":
            return self._to_oven_update()
        return self._to_sous_vide_update()

    def _to_oven_update(self) -> OvenUpdate:
        """Convert oven state to OvenUpdate."""
        state = build_oven_state_body(self.state)
        return OvenUpdate.from_state(state)

    def _to_sous_vide_update(self) -> APCUpdate:
        """Convert device state to APCUpdate."""
        binary = APCUpdateBinary(
            cooking=self.state.get("mode", "") in ["COOKING", "PREHEATING"],
            preheating=self.state.get("mode", "") == "PREHEATING",
            maintaining=self.state.get("mode", "") == "MAINTAINING",
            device_safe=self.state.get("device_safe", True),
            water_leak=self.state.get("water_leak", False),
            water_level_critical=self.state.get("water_level_critical", False),
            water_temp_too_high=self.state.get("water_temp_too_high", False),
            water_level_low=self.state.get("water_level_low", False),
        )
        sensor = APCUpdateSensor(
            target_temperature=float(self.state.get("target_temp", 0)),
            current_temperature=float(self.state.get("current_temp", 0)),
            state=self.state.get("mode", ""),
            cook_time=int(self.state.get("timer_value", 0)),
            cook_time_remaining=int(self.state.get("timer_value_remaining", 0)),
            mode=self.state.get("mode", ""),
            a3_state=None,
        )
        return APCUpdate(binary_sensor=binary, sensor=sensor)

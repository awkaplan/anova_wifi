from anova_wifi.web_socket_containers import (
    AnovaA3State,
    AnovaState,
    APCUpdate,
    APCWifiDevice,
    OvenMode,
    OvenStage,
    OvenUpdate,
    build_a3_payload,
    build_a6_a7_payload,
    build_oven_state_body,
    build_wifi_cooker_state_body,
)
from tests.example_data import (
    A3_MESSAGE,
    A4_MESSAGE,
    A6_MESSAGE,
    A7_COOKING,
    A7_MESSAGE,
)


def test_a3_payload():
    resp = build_a3_payload(A3_MESSAGE["payload"]["state"])
    # Ensure some of the basics
    assert resp.sensor.target_temperature == 96.1
    assert resp.sensor.a3_state == AnovaA3State.cooking.name
    assert resp.sensor.cook_time_remaining == 840


def test_a4_payload():
    resp = build_wifi_cooker_state_body(A4_MESSAGE["payload"]["state"]).to_apc_update()
    # Ensure some of the basics
    assert resp.sensor.target_temperature == 66.11
    assert resp.sensor.state == AnovaState.cooking.name
    assert resp.sensor.cook_time_remaining == 0


def test_a7_payload():
    resp = build_a6_a7_payload(A7_MESSAGE["payload"]["state"])
    assert resp.sensor.mode == "idle"
    assert resp.sensor.cook_time == 36000


def test_a7_cooking():
    resp = build_a6_a7_payload(A7_COOKING["payload"]["state"])
    assert resp.sensor.mode == "cook"
    assert resp.sensor.cook_time == 1200


def test_a6_payload():
    resp = build_a6_a7_payload(A6_MESSAGE["payload"]["state"])
    assert resp.sensor.mode == "idle"
    assert resp.sensor.cook_time == 7200
    assert resp.sensor.target_temperature == 57.2


OVEN_MESSAGE = {
    "mode": "cooking",
    "stage": "steam",
    "target_temp": 180.5,
    "current_temp": 175.2,
    "target_steam": 80,
    "current_steam": 75,
    "timer": 1800,
    "door_open": False,
    "light": True,
    "error_code": None,
}

OVEN_PREHEATING_MESSAGE = {
    "mode": "preheating",
    "target_temp": 200.0,
    "current_temp": 150.3,
    "target_steam": None,
    "current_steam": None,
    "timer": None,
    "door_open": False,
    "light": False,
    "error_code": None,
}


def test_oven_state_cooking():
    """Test parsing oven state during cooking."""
    state = build_oven_state_body(OVEN_MESSAGE)

    assert state.mode == OvenMode.COOKING
    assert state.stage == OvenStage.STEAM
    assert state.target_temperature == 180.5
    assert state.current_temperature == 175.2
    assert state.target_steam == 80
    assert state.current_steam == 75
    assert state.timer_remaining == 1800
    assert not state.door_open
    assert state.light_on
    assert state.error_code is None


def test_oven_state_preheating():
    """Test parsing oven state during preheat."""
    state = build_oven_state_body(OVEN_PREHEATING_MESSAGE)

    assert state.mode == OvenMode.PREHEATING
    assert state.stage is None
    assert state.target_temperature == 200.0
    assert state.current_temperature == 150.3
    assert state.target_steam is None
    assert state.current_steam is None
    assert state.timer_remaining is None
    assert not state.door_open
    assert not state.light_on
    assert state.error_code is None


def test_oven_update_conversion():
    """Test converting oven state to update format."""
    device = APCWifiDevice(
        id="test_oven", name="Test Oven", state=OVEN_MESSAGE, device_type="oven"
    )

    update = device.to_update()
    assert isinstance(update, OvenUpdate)

    # Test binary sensors
    assert update.binary_sensor.cooking is True
    assert update.binary_sensor.preheating is False
    assert update.binary_sensor.door_open is False
    assert update.binary_sensor.light_on is True
    assert update.binary_sensor.error is False

    # Test sensors
    assert update.sensor.mode == "cooking"
    assert update.sensor.stage == "steam"
    assert update.sensor.target_temperature == 180.5
    assert update.sensor.current_temperature == 175.2
    assert update.sensor.target_steam == 80
    assert update.sensor.current_steam == 75
    assert update.sensor.timer_remaining == 1800


def test_oven_error_state():
    """Test parsing oven error state."""
    error_message = {
        "mode": "error",
        "current_temp": 25.0,
        "door_open": False,
        "light": False,
        "error_code": "E01",
    }

    state = build_oven_state_body(error_message)
    assert state.mode == OvenMode.ERROR
    assert state.error_code == "E01"

    device = APCWifiDevice(
        id="test_oven", name="Test Oven", state=error_message, device_type="oven"
    )
    update = device.to_update()
    # Type check the update before accessing error attribute
    from anova_wifi.web_socket_containers import OvenUpdate

    assert isinstance(update, OvenUpdate)
    assert update.binary_sensor.error is True


def test_device_type_detection():
    """Test correct update type based on device type."""
    sous_vide_device = APCWifiDevice(
        id="test_sv", name="Test Sous Vide", state={}, device_type="sous_vide"
    )
    oven_device = APCWifiDevice(
        id="test_oven", name="Test Oven", state={"mode": "error"}, device_type="oven"
    )

    sous_vide_update = sous_vide_device.to_update()
    assert isinstance(sous_vide_update, APCUpdate)

    oven_update = oven_device.to_update()
    assert isinstance(oven_update, OvenUpdate)  # Simplified type check
    assert oven_update.binary_sensor.error is True


from construct import (
    BitStruct,
    Byte,
    Bytes,
    Flag,
    Padding,
    Struct,
)

camera_status_struct = BitStruct(
    "processor_state" / Flag,
    "wifi_ap_state" / Flag,
    "peripheral_pairing_state" / Flag,
    "central_role_enabled" / Flag,
    "is_new_media_available" / Flag,
    "reserved01" / Flag,
    "reserved02" / Flag,
    "reserved03" / Flag,
)


camera_capability_struct = BitStruct(
    "cnc" / Flag,
    "ble_metadata" / Flag,
    "wideband_audio" / Flag,
    "concurrent_master_slave" / Flag,
    "onboarding" / Flag,
    "new_media_available" / Flag,
    "reserved" / Padding(10),
)

media_offload_status_struct = BitStruct(
    "available" / Flag,
    "new_media_available" / Flag,
    "battery_ok" / Flag,
    "sd_card_ok" / Flag,
    "busy" / Flag,
    "paused" / Flag,
    "reserved" / Padding(2),
)

manuf_data_struct = Struct(
    "schema_version" / Byte,
    "camera_status" / camera_status_struct,
    "camera_id" / Byte,
    "camera_capabilities" / camera_capability_struct,
    "id_hash" / Bytes(6),
    "media_offload_status" / media_offload_status_struct,
)

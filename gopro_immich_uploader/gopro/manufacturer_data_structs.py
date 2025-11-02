from construct import (
    BitStruct,
    Byte,
    Bytes,
    Flag,
    Struct,
)
from open_gopro.models.network_scan_responses import camera_capability_struct, media_offload_status_struct

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

manuf_data_struct = Struct(
    "schema_version" / Byte,
    "camera_status" / camera_status_struct,
    "camera_id" / Byte,
    "camera_capabilities" / camera_capability_struct,
    "id_hash" / Bytes(6),
    "media_offload_status" / media_offload_status_struct,
)

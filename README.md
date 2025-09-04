# Automatic GoPro Media Uploader for Immich

Ever wondered why your feature-packed GoPro can't just connect to your own server and upload all the media automatically? Me too. Luckily, both GoPro and Immich have a convenient API. So I created this lil service to do just that. (Yee, I know there is the cloud subscription.)

## What does it do?

- The service scans the BLE network for paired GoPro cameras.
- When a camera is detected, we set it up for [COHM (Camera On the Home Network)](https://gopro.github.io/OpenGoPro/ble/features/cohn.html) and instruct it to connect to your home Wi-Fi network.
- Once connected, the service streams media, one by one, directly from the camera to the Immich server (without storing in RAM or on disk).
- All media confirmed to be uploaded by Immich are automatically deleted from the camera (configurable).
- When all media are uploaded, the camera is powered off.

## Why?

I wanna be lazy. Downloading footage to my PC to upload to Immich was too much work and caused too many worn-out SSD bits to get immediately deleted once uploaded.

## How?

- Use a Linux machine with Docker and BlueZ installed.
- Ensure your Linux machine is paired with your GoPro, which you can do using the `bluetoothctl` command.
- Launch the service with this command:
```sh
docker run --rm --name gopro-immich-uploader \
  -e IMMICH_API_KEY=your-api-key \
  -e IMMICH_SERVER_URL=https://yourimmich.example.com/api \
  -v /run/dbus:/run/dbus:ro
```

## Development setup

- Install Python dependencies:
```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
- Run the service:
```sh
python -m gopro_immich_uploader
```
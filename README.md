# Automatic GoPro Media Uploader for Immich

Have you ever wondered why your feature-packed GoPro can't just connect to your own server and upload all the media automatically?
Me too. Luckily, both GoPro and Immich have a convenient API. So I created this lil service to do just that.
(Yee, I know there is the cloud subscription.)

## What does it do?

- The service scans the BLE network for paired GoPro cameras.
- When a camera is detected, we set it up for [COHM (Camera On the Home Network)](https://gopro.github.io/OpenGoPro/ble/features/cohn.html) and instruct it to connect to your home Wi-Fi network.
- Once connected, the service streams media, one by one, directly from the camera to the Immich server (without storing in RAM or on disk).
- All media confirmed to be uploaded by Immich are automatically deleted from the camera (configurable).
- When all media are uploaded, the camera is powered off (configurable).

## Why?

I wanna be lazy. Downloading footage to my PC just to upload it to Immich was too much work and caused too many worn-out SSD bits to be immediately deleted once uploaded.

## How?

- Use a Linux machine with Docker (or Podman) and BlueZ installed.
- Ensure your Linux machine is paired with your GoPro, which you can do using the `bluetoothctl` command. See [Pairing with GoPro](#pairing-with-gopro).
- Launch the service with this command:
```sh
docker run --rm --read-only --name gopro-immich-uploader \
  -e IMMICH_API_KEY=your-api-key \
  -e IMMICH_SERVER_URL=https://yourimmich.example.com/api \
  -e WIFI_SSID=YourHomeWifi \
  -e WIFI_PASSWORD=YourWifiPassword \
  -e DELETE_AFTER_UPLOAD=true \
  -e SCAN_INTERVAL_SEC=30 \
  -e CAMERA_POWER_OFF=true \
  -e LOG_LEVEL=INFO \
  -v /run/dbus:/run/dbus:ro \
  docker.io/anty0/gopro-auto-immich-upload:1.0.0
```

### Environment variables

- `IMMICH_SERVER_URL`: Immich API base URL, e.g., https://immich.example.com/api (default: http://127.0.0.1:2283/api)
- `IMMICH_API_KEY`: Immich API key (required)
- `WIFI_SSID`: Home Wi-Fi SSID (required)
- `WIFI_PASSWORD`: Home Wi-Fi password (required)
- `DELETE_AFTER_UPLOAD`: Delete media on camera after successful upload (true/false, default false)
- `SCAN_INTERVAL_SEC`: Scan interval in seconds for BLE scanning (int > 0, default 30)
- `CAMERA_POWER_OFF`: Power off camera after uploads complete (true/false, default false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL; default INFO)

## Pairing with GoPro

```sh
bluetoothctl
[bluetoothctl]> power on
[bluetoothctl]> scan le
[bluetoothctl]> devices
# Find your GoPro in the list
[bluetoothctl]> pair <GoPro MAC address>
# Repeat the last command until you see "Pairing successful"
[bluetoothctl]> quit
```

## Development setup

- Install Python dependencies:
```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
- Run the service:
```sh
export IMMICH_API_KEY=your-api-key
export IMMICH_SERVER_URL=https://yourimmich.example.com/api
export WIFI_SSID=YourHomeWifi
export WIFI_PASSWORD=YourWifiPassword
export DELETE_AFTER_UPLOAD=true
export SCAN_INTERVAL_SEC=30
export CAMERA_POWER_OFF=true
export LOG_LEVEL=INFO
python -m gopro_immich_uploader
```

## Limitations

- Only raw media are uploaded; all other files and metadata are ignored.
- Tested only on Linux with GoPro 13

## Disclaimer

This is not affiliated with GoPro in any way.

I am not responsible for any damage caused by this project.
Don't trust this code to take care of your precious footage.
**Especially** if you enable the `DELETE_AFTER_UPLOAD` option.
If the Immich faints and your footage gets deleted anyway, you're on your own.

I use this thing to automatically pull "DashCam" like footage from the camera.
I won't notice if a video disappears from time to time, but you might.

While OpenGoPro is a great resource for implementing your own GoPro library, I've quickly
learned that it is awful when used as a library. Examples of things I had to
work around:
- Even though I don't use the AP mode - I don't need the library to touch Wi-Fi (my server doesn't even have one), the
  library tries to play around with nmcli and asks for a sudo password. Solved by implementing a no-op version of the Wi-Fi controller.
- OpenGoPro stores COHN configuration in a file on disk. Since I want this app to run in a read-only Docker container, I don't want
  it to write into any files—I'd much rather get this config as a dict and pass it when initializing the COHN instance.
  Solved by overriding the default storage backend of the `tinydb` to store the database in memory.
- The library tries to check if the camera is paired, but fails miserably on my machine, because the prompt of the `bluetoothctl`
  command does not contain `#`. Actually, all of these "let's run a command and parse its output" things are just minefields waiting to explode.
- I didn't find a way to detect whether the camera is powered on or not using the library. I need to avoid waking it up by connecting to it.
  I ended up overriding the BLE controller to hook when the library tried to connect to read random BLE advertisements to figure out
  whether the camera was powered on or not from an undocumented flag bit. I still believe there is something wrong with that code.
  All the manufacturer data I'm getting does not make any sense. If you are still reading this, and you can find what's wrong,
  please let me know.
- To implement streaming downloads of media, I ended up creating a custom mixin and fitting it nicely between the `WirelessGoPro`
  and `GoProBase` classes. To pass the stream, I ended up abusing the property used to pass the file name.
- Since I'm ranting on libs, why not add that `requests_toolbelt` reports the full length of the body, while requests expect
  only the remaining length? Had to patch up the `StreamingIterator` to get it to work.

All of these should stand as a reason this whole thing should be rewritten from scratch using better libraries.
But it works well enough for my needs.

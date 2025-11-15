# Automatic GoPro Media Uploader for Immich

Have you ever wondered why your feature-packed GoPro can't just connect to your own server and upload all the media automatically?
Me too. Luckily, both GoPro and Immich have a convenient API. So I created this lil service to do just that.
(Yee, I know there is the cloud subscription.)

## What does it do?

- It scans the BLE network for GoPro cameras.
- Then we set it up for [COHM (Camera On the Home Network)](https://gopro.github.io/OpenGoPro/ble/features/cohn.html) and instruct it to connect to your home Wi-Fi network.
- Every time the camera is connected to the Wi-Fi, the service streams media, one by one, directly from the camera to the Immich server (without storing in RAM or on disk).
- All media confirmed to be uploaded by Immich are automatically deleted from the camera (configurable).
- When all media are uploaded, the camera is put to sleep (configurable).

## Why?

Downloading footage to my PC just to upload it to Immich was annoying and caused too many worn-out SSD bits for my taste.

## How?

Use a Linux machine with Docker (or Podman) and BlueZ installed.

### Step 1: Setup the Camera (One-Time)

Pair your Linux machine with your GoPro. You can do so using the `bluetoothctl` command. See [Pairing with GoPro](#pairing-with-gopro).
Run the setup command to provision your GoPro for COHN (Camera On the Home Network):

```sh
docker run --rm -it --name gopro-immich-setup \
  -e WIFI_SSID=YourHomeWifi \
  -e WIFI_PASSWORD=YourWifiPassword \
  -v /run/dbus:/run/dbus:ro \
  docker.io/anty0/gopro-auto-immich-upload:latest \
  setup --no-pair
```

> [!IMPORTANT]
> Pairing via Bluetooth needs to be done manually on modern Linux machines.
> The integrated pairing support in the OpenGoPro library is broken.

Copy the `IDENTIFIER=...` and `COHN_CREDENTIALS=...` lines from the output - you'll need it in the next step.

### Step 2: Run the service

Once you have the COHN credentials from Step 1, launch the service with:

```sh
docker run --rm --read-only --name gopro-immich-uploader \
  -e IMMICH_API_KEY=your-api-key \
  -e IMMICH_SERVER_URL=https://yourimmich.example.com/api \
  -e IDENTIFIER=<identifier_from_setup> \
  -e COHN_CREDENTIALS=<base64_credentials_from_setup> \
  docker.io/anty0/gopro-auto-immich-upload:latest
```

### Environment Variables

**For Setup:**
- `WIFI_SSID`: Home Wi-Fi SSID (required)
- `WIFI_PASSWORD`: Home Wi-Fi password (required)
- `IDENTIFIER`: Camera identifier (optional)
- `NO_PAIR`: Don't pair the camera with bluetooth adapter the server (true/false, default false)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL; default INFO)

**For Service:**
- `IMMICH_SERVER_URL`: Immich API base URL, e.g., https://immich.example.com/api (default: http://127.0.0.1:2283/api)
- `IMMICH_API_KEY`: Immich API key (required)
- `IDENTIFIER`: Camera identifier (required)
- `COHN_CREDENTIALS`: Base64-encoded COHN credentials from setup command (required)
- `DELETE_AFTER_UPLOAD`: Delete media on camera after successful upload (true/false, default false)
- `SCAN_INTERVAL_SEC`: Scan interval in seconds for checking new media (int > 0, default 30)
- `CAMERA_SLEEP`: Sleep after uploading all media (true/false, default true)
- `MIN_BATTERY_LEVEL`: Minimum battery level percentage for setup (int 0-100, default 20)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL; default INFO)

> [!NOTE]
> The OpenGoPro library logs a lot of debug garbage in the INFO log level channel.
> To separate this garbage from the actual INFO logs, the service logs most of the INFO logs as WARNING.
> I'm sorry...

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

## Development Setup

Install Python dependencies:
```sh
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Check code (format, lint, type check, etc.):
```sh
# Format code
ruff format .

# Lint
ruff check --fix .

# Type check
mypy gopro_immich_uploader
```

Run the setup command:
```sh
export WIFI_SSID=YourHomeWifi
export WIFI_PASSWORD=YourWifiPassword
export LOG_LEVEL=DEBUG
python -m gopro_immich_uploader setup --no-pair
```

Copy the `COHN_CREDENTIALS` output and run the main loop:
```sh
export IMMICH_SERVER_URL=https://yourimmich.example.com/api
export IMMICH_API_KEY=your-api-key
export IDENTIFIER=<output_from_setup>
export COHN_CREDENTIALS=<output_from_setup>
export DELETE_AFTER_UPLOAD=true
export SCAN_INTERVAL_SEC=30
export CAMERA_SLEEP=false
export MIN_BATTERY_LEVEL=0
export LOG_LEVEL=DEBUG
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
  command does not contain `#` character. Actually, all of these "let's run a command and parse its output" things are just minefields waiting to explode.
- The GoPro camera sometimes forgets Bluetooth pairing for no apparent reason. In the first version I relied on camera staying paired to the
  server. That way I can just power on the camera, and everything else would happen automatically. Instead I had to pair the camera with the server
  every few days. To make the matter worse, it is only possible to pair the camera on the "Pair device" screen, so there is no way of automating this.
  I ended up splitting off the BLE setup to a separate step. I just hope the camera won't be forgetting the COHN setup now instead...
- I didn't find a way to detect whether the camera is powered on or not using the library. I need to avoid waking it up by connecting to it.
  I ended up overriding the BLE controller to hook when the library tried to connect to read random BLE advertisements to figure out
  whether the camera was powered on or not from an undocumented flag bit. I still believe there is something wrong with that code.
  All the manufacturer data I'm getting does not make any sense. If you are still reading this, and you can find what's wrong,
  please let me know.
- The "delete file" endpoint on GoPro is unreliable. It fails for no apparent reason (returns non-200 status). After many attempts,
  I've found that disabling the turbo mode makes this endpoint work reliably again.
- The power off and sleep http endpoints are missing from the public OpenApi spec. After asking myself "Why there is a reboot endpoint, but not a power off endpoint?"
  I figured I might as well try calling some undocumented http endpoints to see if any of them work. They did work. So now I can put the camera to sleep over http.
- To implement streaming downloads of media, I ended up creating a custom mixin and fitting it nicely between the `WirelessGoPro`
  and `GoProBase` classes. To pass the stream, I ended up abusing the property used to pass the file name.
- Since I'm ranting on libs, why not add that `requests_toolbelt` reports the full length of the body, while requests expect
  only the remaining length? Had to patch up the `StreamingIterator` to get it to work.

All of these should stand as a reason this whole thing should be rewritten from scratch using better libraries.
But it works well enough for my needs.

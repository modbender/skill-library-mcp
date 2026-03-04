# Examples

List devices (bash):

SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... scripts/list_devices.sh

Get status:

SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... scripts/get_status.sh E1AA22334455

Send command (turn on):

SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... scripts/send_command.sh E1AA22334455 turnOn

Curtain to 50%:

# The CLI will send parameter "0,ff,50" automatically
SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... node scripts/switchbot_cli.js cmd E1AA22334455 setPosition --pos=50

Device via Scene (when direct commands are unknown):

SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... skills/public/switchbot-openapi/scripts/list_scenes.sh
# find your "Vacuum Start" sceneId in output, then:
SWITCHBOT_TOKEN=... SWITCHBOT_SECRET=... skills/public/switchbot-openapi/scripts/execute_scene.sh <sceneId>

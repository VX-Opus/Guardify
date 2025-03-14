#!/bin/bash

set -e

if [ -z "$PORT" ]; then
  echo "ᴘᴏʀᴛ ɪꜱ ɴᴏᴛ ꜱᴇᴛ. ᴠx ᴀɪ ɪꜱ ᴅᴇꜰᴀᴜʟᴛɪɴɢ ᴛᴏ 8080 🌐"
  PORT=8080
fi

if [ -z "$FLASK_APP" ]; then
  echo "ꜰʟᴀꜱᴋ ᴀᴘᴘ ɪꜱ ɴᴏᴛ ꜱᴇᴛ. [ᴠx ᴀɪ] ɪꜱ ᴅɪʀᴇᴄᴛʟʏ ʙᴏᴏᴛɪɴɢ ᴛᴏ ɪᴛꜱ ꜱᴇʀᴠᴇʀ ꜰʟᴀꜱᴋ ⚡"
  export FLASK_APP=vxcore:create_app
fi

function shutdown {
    echo "ᴇxᴇᴄᴜᴛɪɴɢ ᴀ ꜱᴍᴏᴏᴛʜ ᴇxɪᴛ... ʙʀɪɴɢɪɴɢ ᴛʜᴇ ꜱᴛᴏʀᴍ ʙᴏᴛ ᴛᴏ ᴀ ꜱᴀꜰᴇ ʜᴀʟᴛ 🌪️"
    kill -TERM "$gunicorn_pid" 2>/dev/null
    wait "$gunicorn_pid"
    echo "ꜰᴏᴜɴᴅ ᴀ ꜱᴇʀᴠᴇʀ ᴇʀʀᴏʀ. ʏᴏᴜʀ ᴅᴇᴘʟᴏʏᴍᴇɴᴛ ᴍᴀʏ ɴᴏᴛ ʙᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴛʜᴇ ᴠx'ꜱ ꜱᴇʀᴠᴇʀ. ꜱʜᴜᴛᴛɪɴɢ ᴅᴏᴡɴ ᴛʜᴇ ᴅᴇᴘʟᴏʏᴍᴇɴᴛ ᴛᴏ ᴋᴇᴇᴘ ʏᴏᴜʀ ʙᴏᴛ ꜱᴀꜰᴇ... 🔒"
}

trap shutdown SIGTERM

gunicorn -w 4 -b 0.0.0.0:$PORT kex:create_app &
gunicorn_pid=$!

echo "ꜱᴛᴀʀᴛɪɴɢ ʏᴏᴜʀ ᴠx ʙᴏᴛ [ᴠᴇʀꜱɪᴏɴ ᴠ1] ⚡"
python3 main.py >> main.log 2>&1 &

wait "$gunicorn_pid"

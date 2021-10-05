#!/bin/bash

function ts {
  echo [`date '+%Y-%m-%d %H:%M:%S'`] MASTER:
}

echo "$(ts) Starting master controller"

readarray -t CONFIG_FILES < <(ls /config/*.ini)

# If there is no config file copy the default one
if [[ "$CONFIG_FILES" == "" ]]
then
  echo "$(ts) No config files found. Exiting."
  exit 1
fi

for CONFIG_FILE in "${CONFIG_FILES[@]}"
do
  FILENAME=$(basename "$CONFIG_FILE")

  echo "$(ts) Creating monitor for $FILENAME"

  FILEBASE="${FILENAME%.*}"

  mkdir -p /etc/service/$FILEBASE

  cat > /etc/service/$FILEBASE/run <<EOF
#!/bin/bash

python3 -m monitor "$CONFIG_FILE"
EOF

  chmod a+x /etc/service/$FILEBASE/run
done

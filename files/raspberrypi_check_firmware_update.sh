#!/usr/bin/env bash

# try to load configuration values from rpi update script
RPI_UPDATE=`which rpi-update`

if command -v "$RPI_UPDATE" >/dev/null 2>&1; then
  source <(grep --extended-regexp '^[A-Z_]+=' "$RPI_UPDATE") 
else
  REPO_API=https://api.github.com/repos/Hexxeh/rpi-firmware/git/refs/heads/master
  GITREV=$(curl -s ${REPO_API} | awk '{ if ($1 == "\"sha\":") { print substr($2, 2, 40) } }')
fi

FW_REVFILE="${FW_REVFILE:-/boot/.firmware_revision}"

# without revfile
if [[ ! -f "${FW_REVFILE}" ]]; then
  echo 1
  exit 1
else
  # no update available
  if [[ $(cat "${FW_REVFILE}") == "$GITREV" ]]; then
    echo -n 0
  # update available
  else
    echo -n 1
  fi
fi
exit 0

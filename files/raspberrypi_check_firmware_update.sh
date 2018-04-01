#!/usr/bin/env bash

# try to load configuration values from rpi update script
RPI_UPDATE=`which rpi-update`
CURL_OPTS='--max-time 3'
VERBOSE=0

# Print a msg to stdout if simple verbose is set
# param[in](string) : the msg to write in stdout
function verbose() {
  if [[ "${VERBOSE}" -eq 1 ]]; then
    echo -e "$@"
  fi
}

function debug() {
  if [[ "${DEBUG}" -eq 1 ]]; then
    echo -e "DEBUG: $@"
  fi
}

# Print a msg to stderr
# param[in](string) : the msg to write in stderr
function error() {
  echo "ERROR: $@" 1>&2
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -v|--verbose)
      VERBOSE=1
      shift 1
      ;;
    --debug)
      VERBOSE=1
      DEBUG=1
      shift 1
      ;;
    --)
      shift 1
      arguments=$@
      break;
      ;;
    *)    # unknown option
      error "error unknown option $1"
      exit 1
      ;;
  esac
done

# Main

# Manually parse environement file because sudo may not use login by default
if [[ -f /etc/environment ]]; then
  while read line; do
    export "${line}"
  done < /etc/environment
fi

if command -v "$RPI_UPDATE" >/dev/null 2>&1; then
  # Source functions
  source <(sed -n '/function /,/^}/p' "$RPI_UPDATE")
  # Source variables
  source <(grep --extended-regexp '^[A-Z_]+=' "$RPI_UPDATE")
fi

# GITREV must be filled
if [ -z "$GITREV" ]; then
  REPO_API=https://api.github.com/repos/Hexxeh/rpi-firmware/git/refs/heads/master
  GITREV=$(curl $CURL_OPTS --silent "${REPO_API}" | awk '{ if ($1 == "\"sha\":") { print substr($2, 2, 40) } }')
  verbose "fetched remote revision from github : ${GITREV}"
fi

FW_REVFILE="${FW_REVFILE:-/boot/.firmware_revision}"

# without revfile
if [[ ! -f "${FW_REVFILE}" ]]; then
  echo 'Firmware revision file not found' 1>&2
  echo 'FIRMWARE UPDATE_AVAILABLE'
  exit 1
else
  local_revision=$(cat "${FW_REVFILE}")
  verbose "fetched local revision from ${FW_REVFILE} : ${GITREV}"

  # no update available
  if [[ "${local_revision}" == "${GITREV}" ]]; then
    echo 'FIRMWARE UP_TO_DATE'
  # update available
  else
    echo 'FIRMWARE UPDATE_AVAILABLE'
  fi
fi
exit 0

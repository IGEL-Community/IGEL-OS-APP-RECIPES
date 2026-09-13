#!/bin/bash
#set -x
#trap read debug

ACTION="elastic_agent_postinst"

# Send all stdout/stderr from this script to journald/syslog
exec > >(logger -t "$ACTION") 2>&1

echo "Start"

#From the path: `/services/elastic_agent/var/lib/elastic-agent/data/elastic-agent-9.5.3-0e70ce/elastic-agent`

AGENT_PATH=$(compgen -G /services/elastic_agent/var/lib/elastic-agent/data/elastic-agent-*/elastic-agent)
PARENT_DIR=$(basename "$(dirname "$AGENT_PATH")")
INFO="${PARENT_DIR#elastic-agent-}"
version_dir="${INFO%-*}"
commit_hash="${INFO##*-}"

#commit_hash="0e70ce"
#version_dir="9.5.3"

symlink_dir="/usr/share/elastic-agent/bin"
new_agent_dir="/var/lib/elastic-agent/data/elastic-agent-$version_dir-$commit_hash"
new_endpoint_component_bin="$new_agent_dir/components/endpoint-security"

default_symlink="/usr/share/elastic-agent/bin/elastic-agent"

SERVICE_NAME="ElasticEndpoint"
should_restart_endpoint=false

mkdir -p "$symlink_dir"
ln -svf "$new_agent_dir/elastic-agent" "$default_symlink"

$new_agent_dir/elastic-agent apply-flavor

FLEET_URL=$(getsysvalue app.elastic_agent.config.url)
ENROLLMENT_TOKEN=$(getsysvalue app.elastic_agent.config.enrollment-token)

echo "cp /etc/elastic-agent/* /services/elastic_agent/var/lib/elastic-agent"
cp /etc/elastic-agent/* /services/elastic_agent/var/lib/elastic-agent

if [ -n "$FLEET_URL" ] && [ -n "$ENROLLMENT_TOKEN" ]; then
  #
  # If enrolling into Fleet, then need to figure out how to handle the changed files / folders after enrollment.
  #
  if [ ! -f /services_rw/elastic_agent/enrolled ]; then
    echo "Elastic Agent is not enrolled, enrolling now..."
    $new_agent_dir/elastic-agent enroll \
      --url=$FLEET_URL \
      --enrollment-token=$ENROLLMENT_TOKEN
    echo "Need to figure out the changed files after enrollment and copy them to /services_rw/elastic_agent/changed-files"
    #echo $(date) > /services_rw/elastic_agent/enrolled
    echo "mkdir -p /services_rw/elastic_agent/changed-files"
    # mkdir -p /services_rw/elastic_agent/changed-files
  else
    echo "Need to copy the changed files back into /services/elastic_agent/var/lib/elastic-agent"
  fi
fi

echo "Finished"
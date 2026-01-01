#!/bin/bash
# For root services:
enable_system_service docker.socket
enable_system_service containerd.service
enable_system_service docker.service
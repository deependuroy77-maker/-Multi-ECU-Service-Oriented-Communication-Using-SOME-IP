#!/usr/bin/env bash
set -e
echo "Python:"; python3 --version
echo "someipyd:"; command -v someipyd || true
echo "someipy package:"
python3 -m pip show someipy || true
echo "Loopback:"
ip addr show lo
echo "Wireshark:"
command -v wireshark || true

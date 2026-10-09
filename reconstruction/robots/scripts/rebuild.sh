#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p upstream
fetch_pin() {
  local name="$1" url="$2" sha="$3"
  if [ ! -d "upstream/$name/.git" ]; then git clone --filter=blob:none --no-checkout "$url" "upstream/$name"; fi
  git -C "upstream/$name" fetch origin "$sha"
  git -C "upstream/$name" checkout --detach "$sha"
  test "$(git -C "upstream/$name" rev-parse HEAD)" = "$sha"
}
fetch_pin ur https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git 6662e15f32c23c12ece57d0050aee9a716e4fc41
fetch_pin robotiq https://github.com/Robotiq/ros.git adb20dc0048ff2ef51c5a86fe2f7880a8618f099
export PYTHONPATH="$(pwd)/.deps${PYTHONPATH:+:$PYTHONPATH}"
python scripts/build_metadata.py
python scripts/convert_meshes.py
python tests/validate_assets.py

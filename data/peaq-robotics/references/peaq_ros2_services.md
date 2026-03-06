# peaq-robotics-ros2 service map (quick reference)

## Node startup (typical)

- Core node (lifecycle): `core-start` -> `core-configure` -> `core-activate`
- Storage bridge: `storage-start`
- Events node (optional): `events-start`
- Humanoid bridge (optional): `humanoid-start`

All start commands in this skill map to:

- `ros2 run peaq_ros2_core core_node --ros-args -p config.yaml_path:=<config>`
- `ros2 run peaq_ros2_core storage_bridge_node --ros-args -p config.yaml_path:=<config>`
- `ros2 run peaq_ros2_core events_node --ros-args -p config.yaml_path:=<config>`
- `ros2 run peaq_ros2_humanoids humanoid_bridge_node --ros-args -p config.yaml_path:=<config>`

## Core node services

Node namespace is `/peaq_core_node` by default.

- DID create: `/peaq_core_node/identity/create` (IdentityCreate)
  - Request: `{metadata_json: '{"type":"robot"}'}` (default metadata if omitted)
  - If `metadata_json` looks like a DID document (id/controller/services/verificationMethods/authentications/signature), it is used directly.
  - Otherwise it is wrapped into a DID `services` entry (`type: peaqMetadata`) so metadata is preserved.
- DID read: `/peaq_core_node/identity/read` (IdentityRead)
- Store add: `/peaq_core_node/storage/add` (StoreAddData)
  - Request: `{key: 'sensor_data', value_json: '{"temp":25.5}', mode: 'FAST'}`
- Store read: `/peaq_core_node/storage/read` (StoreReadData)
- Access create role: `/peaq_core_node/access/create_role` (AccessCreateRole)
- Access create permission: `/peaq_core_node/access/create_permission` (AccessCreatePermission)
- Access assign permission: `/peaq_core_node/access/assign_permission` (AccessAssignPermToRole)
- Access grant role: `/peaq_core_node/access/grant_role` (AccessGrantRole)
- Info: `/peaq_core_node/info` (GetNodeInfo)
  - Response JSON includes `wallet_address` and `did`.
  - Helper commands: `core-info-json`, `core-address`, `core-did`.

## Storage ingest topic

Publish to the ingest topic for storage bridge:

- Topic: `/peaq/storage/ingest`
- Type: `peaq_ros2_interfaces/msg/StorageIngest`
- Example:
  - `{key: 'sensor_data', is_file: false, file_path: '', content: 'temperature:25.5', content_type: 'text/plain', metadata_json: '{"source":"demo"}'}`

## Environment variables used by the helper script

- `PEAQ_ROS2_ROOT` (repo root)
- `PEAQ_ROS2_CONFIG_YAML` (path to peaq_robot.yaml)
- `ROS_DOMAIN_ID` (ROS 2 domain isolation)
- `PEAQ_ROS2_*_NODE_NAME` (override default node names)
- `PEAQ_ROS2_LOG_DIR`, `PEAQ_ROS2_PID_DIR` (background run metadata)

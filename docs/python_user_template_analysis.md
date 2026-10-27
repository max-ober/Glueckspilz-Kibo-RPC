# Python User Logic: Inputs, Outputs, and Data Contracts

## 1. Purpose

This document analyzes the existing Python user logic and its ROS interfaces.

The objective is to document the current inputs, outputs, communication mechanisms, and known limitations to support the initial software architecture.

This document describes the existing implementation. It does not introduce new interfaces or modify the robot control logic.

## 2. Scope

Main implementation in the local simulator:

`users/catkin_ws/src/krpc_user/scripts/user_template.py`

The interface definitions below were inspected in the local simulator project.

Service definitions:

- `users/catkin_ws/src/krpc_ib2_msgs/srv/CheckPoints.srv`
- `users/catkin_ws/src/krpc_ib2_msgs/srv/MissionStart.srv`
- `users/catkin_ws/src/krpc_ib2_msgs/srv/MissionFinished.srv`

Action definition:

- `users/catkin_ws/src/krpc_ib2_msgs/action/CheckpointPassed.action`
- `docker/ros_overlay/src/ib2_msgs/action/CtlCommand.action`

Navigation message definition:

- `docker/ros_overlay/src/ib2_msgs/msg/Navigation.msg`

These paths refer to the local simulator project, not files currently present in the team repository.

## 3. ROS Interface Inventory

| Interface | Communication | Type | Purpose |
|---|---|---|---|
| `/ib2_user/start` | Subscriber | `platform_msgs/UserLogic` | Receives the user-logic start notification |
| `/ib2_user/stop` | Service server | `platform_msgs/StopProcessingUserNode` | Handles a stop-processing request |
| `/mission/get_checkpoints` | Service client | `krpc_ib2_msgs/CheckPoints` | Requests checkpoint information |
| `/event/mission_start` | Service client | `krpc_ib2_msgs/MissionStart` | Notifies the system that the mission is starting |
| `/event/mission_finished` | Service client | `krpc_ib2_msgs/MissionFinished` | Notifies the system that the mission has finished |
| `/ctl/command` | Action client | `ib2_msgs/CtlCommandAction` | Sends a robot movement command |
| `/event/checkpoint_passed` | Action client | `krpc_ib2_msgs/CheckpointPassedAction` | Reports checkpoint completion |

The interface names and types above are taken from the Python implementation.

The definitions of `UserLogic` and `StopProcessingUserNode` have not yet been located and verified.

The navigation and camera subscribers in the Python template are commented out. They are not active subscriptions in the current implementation.

## 4. Service Contracts

### 4.1 CheckPoints

Definition: `krpc_ib2_msgs/srv/CheckPoints.srv`

Request:

- Empty request; no request fields are defined.

Response:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Indicates whether the request succeeded |
| `message` | `string` | Response information |

The Python implementation attempts to parse `message` as JSON to obtain checkpoint information.

The exact JSON schema has not yet been verified against the service implementation or official documentation.

### 4.2 MissionStart

Definition: `krpc_ib2_msgs/srv/MissionStart.srv`

Request:

- Empty request; no request fields are defined.

Response:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Indicates whether the operation succeeded |
| `message` | `string` | Response information |

The Python implementation checks the `success` field before continuing its user flow.

### 4.3 MissionFinished

Definition: `krpc_ib2_msgs/srv/MissionFinished.srv`

Request:

- Empty request; no request fields are defined.

Response:

| Field | Type | Description |
|---|---|---|
| `success` | `bool` | Indicates whether the operation succeeded |
| `message` | `string` | Response information |

The Python implementation calls this service if the current user flow reaches the end without an earlier failure.

A successful service response alone does not establish that the complete competition mission has been completed successfully.

## 5. CheckpointPassed Action Contract

Definition: `krpc_ib2_msgs/action/CheckpointPassed.action`

| Section | Field | Type | Description |
|---|---|---|---|
| Goal | `checkpoint_id` | `int32` | Checkpoint identifier |
| Result | `success` | `bool` | Indicates whether the operation succeeded |
| Result | `message` | `string` | Result information |
| Feedback | `status` | `string` | Execution status information |

The Python implementation assigns a checkpoint ID to a `CheckpointPassedGoal`, sends the goal, waits for the result, and checks `result.success`.

The server-side acceptance criteria and the exact semantics of the feedback status still require verification.

## 6. Movement Command

Definition in the local simulator:

`docker/ros_overlay/src/ib2_msgs/action/CtlCommand.action`

### 6.1 Goal

| Field | Type | Description |
|---|---|---|
| `target` | `geometry_msgs/PoseStamped` | Target position and orientation, with timestamp and frame information |
| `type` | `CtlStatusType` | Control command type |

The Python implementation creates a `PoseStamped` target and places it in a `CtlCommandGoal`.

The command type is set to `MOVE_TO_ABSOLUTE_TARGET`.

### 6.2 Result

| Field or constant | Type | Description |
|---|---|---|
| `TERMINATE_SUCCESS` | `uint8 = 0` | Successful termination |
| `TERMINATE_ABORTED` | `uint8 = 1` | Aborted command |
| `TERMINATE_TIME_OUT` | `uint8 = 2` | Command timed out |
| `TERMINATE_INVALID_NAV` | `uint8 = 3` | Invalid navigation state |
| `TERMINATE_INVALID_CMD` | `uint8 = 4` | Invalid command |
| `stamp` | `time` | Goal-reached timestamp |
| `type` | `uint8` | Result status |

The Python implementation considers the movement successful when `result.type` equals `CtlCommandResult.TERMINATE_SUCCESS`.

### 6.3 Feedback

| Field | Type | Description |
|---|---|---|
| `time_to_go` | `duration` | Time remaining until the goal |
| `pose_to_go` | `geometry_msgs/Pose` | Described in the source comment as `target - nav`; the exact calculation requires verification |

The expected coordinate frame, position units, quaternion convention, and exact feedback calculation still require verification.

## 7. Navigation Message

Definition in the local simulator:

`docker/ros_overlay/src/ib2_msgs/msg/Navigation.msg`

| Field | Type | Description |
|---|---|---|
| `pose` | `geometry_msgs/PoseStamped` | Position and orientation with header information |
| `twist` | `geometry_msgs/Twist` | Linear and angular velocity |
| `a` | `geometry_msgs/Vector3` | Three-dimensional vector; exact semantics require verification |
| `status` | `NavigationStatus` | Navigation status; the source comment marks it as `TBD` |

The Python template contains a subscriber for `/sensor_fusion/navigation`, but this subscription is commented out.

Therefore, the message definition does not imply that the current user logic actively receives navigation updates.

## 8. Current Execution Flow

Based on the inspected Python implementation, the current flow is:

1. Initialize the ROS node and communication clients.
2. Receive the user-logic start notification.
3. Notify the system that the mission is starting.
4. Request checkpoint information.
5. Select the checkpoint with the smallest ID.
6. Construct a movement target using `PoseStamped`.
7. Send a movement goal through `/ctl/command`.
8. Report checkpoint completion through `/event/checkpoint_passed`.
9. Notify the system that the mission has finished if the preceding steps succeed.

The current flow handles one checkpoint rather than a complete multi-checkpoint traversal.

## 9. Known Limitations and Risks

- Checkpoint retrieval and JSON parsing may fall back to a default target at `(0, 0, 0)`. This behavior should be reviewed because it may cause unintended movement.
- The current user flow handles only one checkpoint.
- The navigation and camera subscribers are commented out.
- The complete definitions of `UserLogic` and `StopProcessingUserNode` have not yet been verified.
- The coordinate frame, position units, and quaternion convention for movement commands remain to be confirmed.
- The exact JSON schema returned in `CheckPoints.message` remains to be confirmed.
- The server-side conditions for accepting a checkpoint as passed require further investigation.

## 10. Testing Evidence

The local simulator has previously executed the Python template and reported a checkpoint-passing event.

This confirms that a checkpoint-passing flow has been observed in the local simulator. It does not establish that full multi-checkpoint mission execution or every interface behavior has been tested.

Additional test results should be recorded as they are performed.

## 11. Open Questions

- What fields are defined in `UserLogic` and `StopProcessingUserNode`?
- What JSON schema is returned in `CheckPoints.message`?
- Which coordinate frame and position units are expected by the movement command?
- What quaternion convention is expected?
- What is the exact calculation of `pose_to_go`?
- What are the server-side conditions for accepting a checkpoint as passed?
- How should invalid checkpoint data and movement failures be handled?
- How should multiple checkpoints be ordered and processed?

## 12. References

- Local simulator: `users/catkin_ws/src/krpc_user/scripts/user_template.py`
- `users/catkin_ws/src/krpc_ib2_msgs/srv/CheckPoints.srv`
- `users/catkin_ws/src/krpc_ib2_msgs/srv/MissionStart.srv`
- `users/catkin_ws/src/krpc_ib2_msgs/srv/MissionFinished.srv`
- `users/catkin_ws/src/krpc_ib2_msgs/action/CheckpointPassed.action`
- `docker/ros_overlay/src/ib2_msgs/action/CtlCommand.action`
- `docker/ros_overlay/src/ib2_msgs/msg/Navigation.msg`
- Kibo-RPC 7th Programming Manual

# -*- coding: utf-8 -*-
# Copyright (c) 2020-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# Copyright (c) 2023 PickNik, LLC. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This Isaac Sim example is derived from
# https://github.com/ros-planning/moveit2_tutorials/blob/efef1d3/doc/how_to_guides/isaac_panda/launch/isaac_moveit.py
# which in turn was derived from an example provided with Isaac Sim 2022.2.1, found at
# standalone_examples/api/omni.isaac.ros2_bridge/moveit.py
#
# flake8: noqa

import sys
import re
import os

import carb
import numpy as np

# In older versions of Isaac Sim (prior to 4.0), SimulationApp is imported from
# omni.isaac.kit rather than isaacsim.
try:
    from isaacsim import SimulationApp
except:
    from omni.isaac.kit import SimulationApp

FRANKA_STAGE_PATH = "/Franka"
FRANKA_USD_PATH = "/Isaac/Robots/Franka/franka_alt_fingers.usd"
CAMERA_PRIM_PATH = f"{FRANKA_STAGE_PATH}/panda_hand/geometry/realsense/realsense_camera"
BACKGROUND_STAGE_PATH = "/background"
BACKGROUND_USD_PATH = "/Isaac/Environments/Simple_Room/simple_room.usd"
GRAPH_PATH = "/ActionGraph"
REALSENSE_VIEWPORT_NAME = "realsense_viewport"

CONFIG = {"renderer": "RayTracedLighting", "headless": False}

simulation_app = SimulationApp(CONFIG)

from omni.isaac.version import get_version

# Check the major version number of Isaac Sim to see if it's four digits, corresponding
# to Isaac Sim 2023.1.1 or older.  The version numbering scheme changed with the
# Isaac Sim 4.0 release in 2024.
is_legacy_isaacsim = (len(get_version()[2]) == 4)

# More imports that need to compare after we create the app
from omni.isaac.core import SimulationContext  # noqa E402
from omni.isaac.core.utils.prims import set_targets
from omni.isaac.core.utils import (  # noqa E402
    extensions,
    nucleus,
    prims,
    rotations,
    stage,
    viewports,
)
from pxr import Gf, UsdGeom  # noqa E402
import omni.graph.core as og  # noqa E402
import omni

# enable ROS2 bridge extension
extensions.enable_extension("omni.isaac.ros2_bridge")

simulation_context = SimulationContext(stage_units_in_meters=1.0)

# Locate Isaac Sim assets folder to load environment and robot stages
assets_root_path = nucleus.get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()

# Preparing stage
viewports.set_camera_view(eye=np.array([1.2, 1.2, 0.8]), target=np.array([0, 0, 0.5]))

# Loading the simple_room environment
stage.add_reference_to_stage(
    assets_root_path + BACKGROUND_USD_PATH, BACKGROUND_STAGE_PATH
)

# Loading the franka robot USD
prims.create_prim(
    FRANKA_STAGE_PATH,
    "Xform",
    position=np.array([0, -0.64, 0]),
    orientation=rotations.gf_rotation_to_np_array(Gf.Rotation(Gf.Vec3d(0, 0, 1), 90)),
    usd_path=assets_root_path + FRANKA_USD_PATH,
)

# add some objects, spread evenly along the X axis
# with a fixed offset from the robot in the Y and Z
prims.create_prim(
    "/cracker_box",
    "Xform",
    position=np.array([-0.2, -0.25, 0.15]),
    orientation=rotations.gf_rotation_to_np_array(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)),
    usd_path=assets_root_path
    + "/Isaac/Props/YCB/Axis_Aligned_Physics/003_cracker_box.usd",
)
prims.create_prim(
    "/sugar_box",
    "Xform",
    position=np.array([-0.07, -0.25, 0.1]),
    orientation=rotations.gf_rotation_to_np_array(Gf.Rotation(Gf.Vec3d(0, 1, 0), -90)),
    usd_path=assets_root_path
    + "/Isaac/Props/YCB/Axis_Aligned_Physics/004_sugar_box.usd",
)
prims.create_prim(
    "/soup_can",
    "Xform",
    position=np.array([0.1, -0.25, 0.10]),
    orientation=rotations.gf_rotation_to_np_array(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)),
    usd_path=assets_root_path
    + "/Isaac/Props/YCB/Axis_Aligned_Physics/005_tomato_soup_can.usd",
)
prims.create_prim(
    "/mustard_bottle",
    "Xform",
    position=np.array([0.0, 0.15, 0.12]),
    orientation=rotations.gf_rotation_to_np_array(Gf.Rotation(Gf.Vec3d(1, 0, 0), -90)),
    usd_path=assets_root_path
    + "/Isaac/Props/YCB/Axis_Aligned_Physics/006_mustard_bottle.usd",
)

simulation_app.update()

try:
    ros_domain_id = int(os.environ["ROS_DOMAIN_ID"])
    print("Using ROS_DOMAIN_ID: ", ros_domain_id)
except ValueError:
    print("Invalid ROS_DOMAIN_ID integer value. Setting value to 0")
    ros_domain_id = 0
except KeyError:
    print("ROS_DOMAIN_ID environment variable is not set. Setting value to 0")
    ros_domain_id = 0

# Create an action graph with ROS component nodes
try:
    og_keys_set_values = [
        ("Context.inputs:domain_id", ros_domain_id),
        # Set the /Franka target prim to Articulation Controller node
        ("ArticulationController.inputs:robotPath", FRANKA_STAGE_PATH),
        ("PublishJointState.inputs:topicName", "isaac_joint_states"),
        ("SubscribeJointState.inputs:topicName", "isaac_joint_commands"),
        ("createViewport.inputs:name", REALSENSE_VIEWPORT_NAME),
        ("createViewport.inputs:viewportId", 1),
        ("cameraHelperRgb.inputs:frameId", "sim_camera"),
        ("cameraHelperRgb.inputs:topicName", "rgb"),
        ("cameraHelperRgb.inputs:type", "rgb"),
        ("cameraHelperInfo.inputs:frameId", "sim_camera"),
        ("cameraHelperInfo.inputs:topicName", "camera_info"),
        ("cameraHelperInfo.inputs:type", "camera_info"),
        ("cameraHelperDepth.inputs:frameId", "sim_camera"),
        ("cameraHelperDepth.inputs:topicName", "depth"),
        ("cameraHelperDepth.inputs:type", "depth"),
    ]

    # In older versions of Isaac Sim, the articulation controller node contained a
    # "usePath" checkbox input that should be enabled.
    if is_legacy_isaacsim:
        og_keys_set_values.insert(1, ("ArticulationController.inputs:usePath", True))

    og.Controller.edit(
        {"graph_path": GRAPH_PATH, "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnImpulseEvent", "omni.graph.action.OnImpulseEvent"),
                ("ReadSimTime", "omni.isaac.core_nodes.IsaacReadSimulationTime"),
                ("Context", "omni.isaac.ros2_bridge.ROS2Context"),
                ("PublishJointState", "omni.isaac.ros2_bridge.ROS2PublishJointState"),
                (
                    "SubscribeJointState",
                    "omni.isaac.ros2_bridge.ROS2SubscribeJointState",
                ),
                (
                    "ArticulationController",
                    "omni.isaac.core_nodes.IsaacArticulationController",
                ),
                ("PublishClock", "omni.isaac.ros2_bridge.ROS2PublishClock"),
                ("OnTick", "omni.graph.action.OnTick"),
                ("createViewport", "omni.isaac.core_nodes.IsaacCreateViewport"),
                (
                    "getRenderProduct",
                    "omni.isaac.core_nodes.IsaacGetViewportRenderProduct",
                ),
                ("setCamera", "omni.isaac.core_nodes.IsaacSetCameraOnRenderProduct"),
                ("cameraHelperRgb", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
                ("cameraHelperInfo", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
                ("cameraHelperDepth", "omni.isaac.ros2_bridge.ROS2CameraHelper"),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnImpulseEvent.outputs:execOut", "PublishJointState.inputs:execIn"),
                ("OnImpulseEvent.outputs:execOut", "SubscribeJointState.inputs:execIn"),
                ("OnImpulseEvent.outputs:execOut", "PublishClock.inputs:execIn"),
                (
                    "OnImpulseEvent.outputs:execOut",
                    "ArticulationController.inputs:execIn",
                ),
                ("Context.outputs:context", "PublishJointState.inputs:context"),
                ("Context.outputs:context", "SubscribeJointState.inputs:context"),
                ("Context.outputs:context", "PublishClock.inputs:context"),
                (
                    "ReadSimTime.outputs:simulationTime",
                    "PublishJointState.inputs:timeStamp",
                ),
                ("ReadSimTime.outputs:simulationTime", "PublishClock.inputs:timeStamp"),
                (
                    "SubscribeJointState.outputs:jointNames",
                    "ArticulationController.inputs:jointNames",
                ),
                (
                    "SubscribeJointState.outputs:positionCommand",
                    "ArticulationController.inputs:positionCommand",
                ),
                (
                    "SubscribeJointState.outputs:velocityCommand",
                    "ArticulationController.inputs:velocityCommand",
                ),
                (
                    "SubscribeJointState.outputs:effortCommand",
                    "ArticulationController.inputs:effortCommand",
                ),
                ("OnTick.outputs:tick", "createViewport.inputs:execIn"),
                ("createViewport.outputs:execOut", "getRenderProduct.inputs:execIn"),
                ("createViewport.outputs:viewport", "getRenderProduct.inputs:viewport"),
                ("getRenderProduct.outputs:execOut", "setCamera.inputs:execIn"),
                (
                    "getRenderProduct.outputs:renderProductPath",
                    "setCamera.inputs:renderProductPath",
                ),
                ("setCamera.outputs:execOut", "cameraHelperRgb.inputs:execIn"),
                ("setCamera.outputs:execOut", "cameraHelperInfo.inputs:execIn"),
                ("setCamera.outputs:execOut", "cameraHelperDepth.inputs:execIn"),
                ("Context.outputs:context", "cameraHelperRgb.inputs:context"),
                ("Context.outputs:context", "cameraHelperInfo.inputs:context"),
                ("Context.outputs:context", "cameraHelperDepth.inputs:context"),
                (
                    "getRenderProduct.outputs:renderProductPath",
                    "cameraHelperRgb.inputs:renderProductPath",
                ),
                (
                    "getRenderProduct.outputs:renderProductPath",
                    "cameraHelperInfo.inputs:renderProductPath",
                ),
                (
                    "getRenderProduct.outputs:renderProductPath",
                    "cameraHelperDepth.inputs:renderProductPath",
                ),
            ],
            og.Controller.Keys.SET_VALUES: og_keys_set_values,
        },
    )
except Exception as e:
    print(e)

simulation_app.update()

# Setting the /Franka target prim to Publish JointState node
set_targets(
    prim=stage.get_current_stage().GetPrimAtPath("/ActionGraph/PublishJointState"),
    attribute="inputs:targetPrim",
    target_prim_paths=[FRANKA_STAGE_PATH],
)

# Fix camera settings since the defaults in the realsense model are inaccurate
realsense_prim = camera_prim = UsdGeom.Camera(
    stage.get_current_stage().GetPrimAtPath(CAMERA_PRIM_PATH)
)
realsense_prim.GetHorizontalApertureAttr().Set(20.955)
realsense_prim.GetVerticalApertureAttr().Set(15.7)
realsense_prim.GetFocalLengthAttr().Set(18.8)
realsense_prim.GetFocusDistanceAttr().Set(400)

set_targets(
    prim=stage.get_current_stage().GetPrimAtPath(GRAPH_PATH + "/setCamera"),
    attribute="inputs:cameraPrim",
    target_prim_paths=[CAMERA_PRIM_PATH],
)

simulation_app.update()

# need to initialize physics getting any articulation..etc
simulation_context.initialize_physics()

simulation_context.play()

# Dock the second camera window
viewport = omni.ui.Workspace.get_window("Viewport")
rs_viewport = omni.ui.Workspace.get_window(REALSENSE_VIEWPORT_NAME)
rs_viewport.dock_in(viewport, omni.ui.DockPosition.RIGHT)


while simulation_app.is_running():

    # Run with a fixed step size
    simulation_context.step(render=True)

    # Tick the Publish/Subscribe JointState, Publish TF and Publish Clock nodes each frame
    og.Controller.set(
        og.Controller.attribute("/ActionGraph/OnImpulseEvent.state:enableImpulse"), True
    )

simulation_context.stop()
simulation_app.close()

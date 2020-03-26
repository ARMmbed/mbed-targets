#
# Copyright (C) 2020 Arm Mbed. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from mbed_targets import MbedTarget


def make_mbed_target(
    board_type="BoardType",
    board_name="BoardName",
    mbed_os_support=None,
    mbed_enabled=None,
    product_code="9999",
    slug="BoardSlug",
    target_type="TargetType",
):
    target_data = {
        "attributes": dict(
            board_type=board_type,
            product_code=product_code,
            name=board_name,
            target_type=target_type,
            slug=slug,
            features=dict(
                mbed_os_support=mbed_os_support if mbed_os_support else (),
                mbed_enabled=mbed_enabled if mbed_enabled else (),
            ),
        )
    }
    return MbedTarget.from_online_target_entry(target_data)


def make_dummy_internal_target_data():
    return [dict(attributes=dict(board_type=str(i), board_name=str(i), product_code=str(i))) for i in range(10)]

# -*- coding: utf-8 -*-
"""
Schedules for br_denatran_frota
"""


from datetime import timedelta, datetime
from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock
from pipelines.constants import constants

every_two_weeks = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(weeks=2),
            start_date=datetime(2021, 1, 1),
            labels=[
                constants.DATASETS_AGENT_LABEL.value,
            ],
        ),
    ]
)

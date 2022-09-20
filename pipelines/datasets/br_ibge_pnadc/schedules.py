# -*- coding: utf-8 -*-
"""
Schedules for br_ibge_pnadc
"""
from datetime import datetime, timedelta

from prefect.schedules import Schedule
from prefect.schedules.clocks import IntervalClock

from pipelines.constants import constants


every_quarter = Schedule(
    clocks=[
        IntervalClock(
            interval=timedelta(days=90),
            start_date=datetime(2021, 1, 1, 15, 0),
            labels=[
                constants.BASEDOSDADOS_DEV_AGENT_LABEL.value,
            ],
            parameter_defaults={
                "dataset_id": "br_ibge_pnadc",
                "table_id": "microdados",
                "auto": True,
                "materialization_mode": "dev",
                "materialize after dump": False,
                "dbt_alias": False,
            },
        )
    ],
)
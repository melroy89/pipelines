# -*- coding: utf-8 -*-
"""
Flows for br_ibge_pnadc
"""
from datetime import datetime, timedelta

from prefect.run_configs import KubernetesRun
from prefect.storage import GCS
from prefect import Parameter, case
from prefect.tasks.prefect import create_flow_run, wait_for_flow_run

from pipelines.utils.execute_dbt_model.constants import constants as dump_db_constants
from pipelines.utils.constants import constants as utils_constants
from pipelines.utils.tasks import (
    create_table_and_upload_to_gcs,
    update_metadata,
    rename_current_flow_run_dataset_table,
    get_current_flow_labels,
)
from pipelines.constants import constants
from pipelines.datasets.br_ibge_pnadc.tasks import (
    crawl,
    clean_save_table,
)
from pipelines.utils.decorators import Flow
from pipelines.datasets.br_ibge_pnadc.schedules import (
    every_three_months,
)

ROOT = "/tmp/data"
URL = "https://ftp.ibge.gov.br/Trabalho_e_Rendimento/Pesquisa_Nacional_por_Amostra_de_Domicilios_continua/Trimestral/Microdados/"


# pylint: disable=C0103
with Flow(
    name="br_ibge_pnadc.microdados", code_owners=["ath67"]
) as br_cgu_pess_exec_fed_terc:
    # Parameters
    dataset_id = Parameter(
        "dataset_id", default="br_ibge_pnadc", required=True
    )
    table_id = Parameter("table_id", default="microdados", required=True)
    materialization_mode = Parameter(
        "materialization_mode", default="dev", required=False
    )
    materialize_after_dump = Parameter(
        "materialize after dump", default=True, required=False
    )

    rename_flow_run = rename_current_flow_run_dataset_table(
        prefix="Dump: ", dataset_id=dataset_id, table_id=table_id, wait=table_id
    )

    crawl_urls = crawl(URL)
    filepath = clean_save_table(ROOT, crawl_urls)

    wait_upload_table = create_table_and_upload_to_gcs(
        data_path=filepath,
        dataset_id=dataset_id,
        table_id=table_id,
        dump_mode="overwrite",
        wait=filepath,
    )

    wait_update_metadata = update_metadata(
        dataset_id=dataset_id,
        table_id=table_id,
        fields_to_update=[
            {"last_updated": {"data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
            {"temporal_coverage": [temporal_coverage]},
        ],
        upstream_tasks=[temporal_coverage],
    )

    with case(materialize_after_dump, True):
        # Trigger DBT flow run
        current_flow_labels = get_current_flow_labels()
        materialization_flow = create_flow_run(
            flow_name=utils_constants.FLOW_EXECUTE_DBT_MODEL_NAME.value,
            project_name=constants.PREFECT_DEFAULT_PROJECT.value,
            parameters={
                "dataset_id": dataset_id,
                "table_id": table_id,
                "mode": materialization_mode,
            },
            labels=current_flow_labels,
            run_name=f"Materialize {dataset_id}.{table_id}",
        )

        wait_for_materialization = wait_for_flow_run(
            materialization_flow,
            stream_states=True,
            stream_logs=True,
            raise_final_state=True,
        )
        wait_for_materialization.max_retries = (
            dump_db_constants.WAIT_FOR_MATERIALIZATION_RETRY_ATTEMPTS.value
        )
        wait_for_materialization.retry_delay = timedelta(
            seconds=dump_db_constants.WAIT_FOR_MATERIALIZATION_RETRY_INTERVAL.value
        )


br_cgu_pess_exec_fed_terc.storage = GCS(constants.GCS_FLOWS_BUCKET.value)
br_cgu_pess_exec_fed_terc.run_config = KubernetesRun(image=constants.DOCKER_IMAGE.value)
br_cgu_pess_exec_fed_terc.schedule = every_three_months

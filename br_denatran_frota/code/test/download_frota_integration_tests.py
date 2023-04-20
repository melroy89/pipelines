import os
import shutil
import tempfile
import unittest
import glob
from parameterized import parameterized
from download_frota import (
    DATASET,
    MONTHS,
    download_frota,
)


class TestDownloadFrota(unittest.TestCase):
    def setUp(self):
        file_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_dir)
        self.temp_dir = tempfile.TemporaryDirectory(dir=file_dir)

    def tearDown(self):
        print("Deleting temporary directory")
        shutil.rmtree(self.temp_dir.name)

    def test_download_frota_with_invalid_month(self):
        with self.assertRaises(ValueError):
            download_frota(13, 2013)

    @parameterized.expand(
        [(month, year) for year in range(2021, 2023) for month in range(1, 12)],
        name_func=custom_name_func,
    )
    def test_download_post_2012(self, month, year):
        download_frota(month, year, self.temp_dir.name)
        expected_files = {
            f"frota_por_uf_e_tipo_de_veículo_{month}-{year}",
            f"frota_por_município_e_tipo_{month}-{year}",
        }
        list_of_files = os.listdir(
            os.path.join(DATASET, self.temp_dir.name, "files", f"{year}")
        )
        files = set(os.path.splitext(file)[0] for file in list_of_files)
        self.assertEqual(files, expected_files)


if __name__ == "__main__":
    unittest.main()

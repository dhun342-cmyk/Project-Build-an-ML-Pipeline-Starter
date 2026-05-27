import pytest
import pandas as pd
import wandb
import os


def pytest_addoption(parser):
    parser.addoption("--csv", action="store")
    parser.addoption("--ref", action="store")
    parser.addoption("--kl_threshold", action="store")
    parser.addoption("--min_price", action="store")
    parser.addoption("--max_price", action="store")


@pytest.fixture(scope='session')
def data(request):
    csv_option = request.config.option.csv

    if csv_option is None:
        pytest.fail("You must provide the --csv option on the command line")

    # If a local file path was provided, load it directly for easier local testing
    if os.path.exists(csv_option):
        return pd.read_csv(csv_option)

    # Otherwise try to download from WandB as an artifact
    run = wandb.init(job_type="data_tests", resume=True)

    try:
        data_path = run.use_artifact(csv_option).file()
    except Exception as e:
        pytest.fail(f"Failed to download CSV artifact '{csv_option}': {e}")

    if data_path is None:
        pytest.fail("Failed to resolve CSV artifact path")

    df = pd.read_csv(data_path)
    return df


@pytest.fixture(scope='session')
def ref_data(request):
    ref_option = request.config.option.ref

    if ref_option is None:
        pytest.fail("You must provide the --ref option on the command line")

    # Allow using a local CSV file as reference for local tests
    if os.path.exists(ref_option):
        return pd.read_csv(ref_option)

    run = wandb.init(job_type="data_tests", resume=True)

    try:
        data_path = run.use_artifact(ref_option).file()
    except Exception as e:
        pytest.fail(f"Failed to download reference artifact '{ref_option}': {e}")

    if data_path is None:
        pytest.fail("Failed to resolve reference artifact path")

    df = pd.read_csv(data_path)
    return df


@pytest.fixture(scope='session')
def kl_threshold(request):
    kl_threshold = request.config.option.kl_threshold

    if kl_threshold is None:
        pytest.fail("You must provide a threshold for the KL test")

    return float(kl_threshold)

@pytest.fixture(scope='session')
def min_price(request):
    min_price = request.config.option.min_price

    if min_price is None:
        pytest.fail("You must provide min_price")

    return float(min_price)

@pytest.fixture(scope='session')
def max_price(request):
    max_price = request.config.option.max_price

    if max_price is None:
        pytest.fail("You must provide max_price")

    return float(max_price)

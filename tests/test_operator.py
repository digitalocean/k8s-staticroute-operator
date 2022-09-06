import subprocess
from kopf.testing import KopfRunner
import time

#####################################
#                                   #
# Not ready yet! Work in progress.  #
#                                   #
#####################################

def setup_function():
    # Create CRD
    subprocess.run(
        "kubectl apply -f controller/config/crd.yaml",
        shell=True,
        check=True
    )
    time.sleep(1)  # give it some time to react


def teardown_function():
    # Delete static route CR used for testing
    subprocess.run(
        "kubectl delete -f tests/manifests/static-route-test.yaml",
        shell=True,
        check=True
    )
    time.sleep(1)  # give it some time to react

    # Delete CRD from cluster
    subprocess.run(
        "kubectl delete -f controller/config/crd.yaml",
        shell=True,
        check=True
    )
    time.sleep(1)  # give it some time to react
    pass


def test_operator():
    with KopfRunner(['run', '--all-namespaces', '--verbose', 'controller/static-route-handler.py']) as runner:
        time.sleep(10) # wait a little bit until controller starts

        # Test static route CR
        subprocess.run(
            "kubectl apply -f tests/manifests/static-route-test.yaml",
            shell=True,
            check=True
        )
        time.sleep(1)  # give it some time to react

    assert runner.exit_code == 0
    assert runner.exception is None
    assert 'Route - dst: 10.42.10.0, gateway: 10.0.2.100 created successfully!' in runner.stdout

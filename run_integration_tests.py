import os

import docker
import logging

from subprocess import run, CalledProcessError

# check_container.py
from typing import Optional



def is_container_running(container_name: str) -> Optional[bool]:
    """Verify the status of a container by it's name

    :param container_name: the name of the container
    :return: boolean or None
    """
    RUNNING = "running"
    # Connect to Docker using the default socket or the configuration
    # in your environment
    docker_client = docker.from_env()
    # Or give configuration
    # docker_socket = "unix://var/run/docker.sock"
    # docker_client = docker.DockerClient(docker_socket)

    try:
        container = docker_client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        return container_state["Status"] == RUNNING


def run_command(command, env=None):
    """ Runs requested process with arguments.
        Return: returncode of executed program.
    """
    logging.debug("Command: {}".format(command))
    try:
        result = run(command, env=env, shell=False, capture_output=False, check=True)
    except FileNotFoundError as bad_cmd:
        print("FileNotFound Error")
        result = False
    except CalledProcessError as exc:
        print("Got Here")
        result = False
    return result


if __name__ == '__main__':
    
    # Check if docker is available
    rc = run_command(['docker', 'info'],env=os.environ)
    if rc:
        # Check if the Minio Server is running
        container_name = "minio_server"
        result = is_container_running(container_name)
    else:
        result = False

    if result or 'GITHUB_ACTIONS' in os.environ:
        rc = run_command(['poetry', 'run', 'pytest', 'tests/integration'],env=os.environ)
        raise SystemExit(rc)
    else:
        print('Skipping Integration Tests - minio is not running')
        print('-------------------------------------------------')
        print('Ensure minio server is running to run these tests.')
        print('You can start minio server by these steps:')
        print('docker compose up -d')
        print('poetry run python run_integration_tests.py')


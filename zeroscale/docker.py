import asyncio
import docker
import logging

from .status import Status
from .base_server import BaseServer

STATUS_MAP = {
    'created': Status.starting,
    'dead': Status.stopped,
    'exited': Status.stopped,
    'paused': Status.paused,
    'removing': Status.stopping,
    'restarting': Status.starting,
    'running': Status.running,
}

logger = logging.getLogger(__name__)


class DockerProxyServer(BaseServer):
    """Docker container interface"""
    def __init__(self,
            container_id: str,
            wrapped_class: BaseServer = None,
        ):

        self.container_id = container_id
        self.wrapped_class = wrapped_class

        self.docker_client = docker.from_env()
        self.status = self.get_container_status()

    def get_container(self):
        try:
            return self.docker_client.containers.get(self.container_id)
        except docker.errors.NotFound:
            logger.critical("Can not manage container that does not exist!")
            raise

    def get_container_status(self):
        container = self.get_container()
        logger.debug("Container status: '%s'", container.status)
        return STATUS_MAP.get(container.status)

    def get_container_healthy(self):
        container = self.get_container()
        try:
            return container.attrs['State']['Health']['Status'] == 'healthy'
        except KeyError:
            # The container doesn't have a health check, so have to pass it
            return True

    async def start(self):
        """Start the Docker container"""

        if self.status is not Status.stopped:
            return

        self.status = Status.starting
        logger.info("Starting container")
        container = self.get_container()
        container.start()
        await self.await_container_healthy()
        self.status = Status.running
        logger.info("Container running")

    async def await_container_healthy(self):
        """Wait for the container to be healthy. A container without a health check
           passes immediately"""

        logger.debug("Waiting for container healthy status")
        while not self.get_container_healthy():
            await asyncio.sleep(.5)

    async def stop(self):
        """Stop the Docker container"""

        if self.status not in (Status.running, Status.paused):
            return False

        logger.info("Stopping container")
        self.status = Status.running
        container = self.get_container()
        container.stop()

    async def pause(self):
        """Pause the Docker container"""

        if self.status not in (Status.starting, Status.running):
            return

        logger.info("Pausing container")
        self.status = Status.paused
        container = self.get_container()

        try:
            container.pause()
        except docker.errors.APIError:
            logger.warn("Container failed to pause")

    async def unpause(self):
        """Unpause the Docker container"""

        if self.status is not Status.paused:
            return

        logger.info("Unpausing container")
        self.status = Status.running
        container = self.get_container()

        try:
            container.unpause()
        except docker.errors.APIError:
            logger.warn("Container failed to unpause")

    def close(self):
        self.docker_client.close()

    async def is_valid_connection(self, client_reader):
        if self.wrapped_class:
            return await self.wrapped_class.is_valid_connection(client_reader)
        else:
            return super().is_valid_connection(client_reader)

    def fake_status(self) -> bytes:
        if self.wrapped_class:
            return self.wrapped_class.fake_status(client_reader)
        else:
            return super().wrapped_class.fake_status(client_reader)

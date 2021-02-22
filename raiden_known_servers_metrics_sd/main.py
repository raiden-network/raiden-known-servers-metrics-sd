import json
import sys
from dataclasses import dataclass
from enum import Enum
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import List

import click
import click_pathlib
import httpx
from httpx import HTTPError
from structlog import get_logger

log = get_logger(__name__)


KNOWN_SERVERS_URL_BASE = (
    "https://raw.githubusercontent.com/raiden-network/raiden-service-bundle/master/known_servers/"
)
KNOWN_SERVERS_URLS = {
    "development": KNOWN_SERVERS_URL_BASE + "known_servers-development-v1.2.0.json",
    "production": KNOWN_SERVERS_URL_BASE + "known_servers-production-v1.2.0.json",
}

KNOWN_SERVERS_URL_METADATA = KNOWN_SERVERS_URL_BASE + "known_servers_metadata.json"


class Services(Enum):
    SYNAPSE = "metrics.transport"
    DB = "metrics.db"
    REDIS = "metrics.redis"
    PFS = "metrics.pfs"
    MS = "metrics.ms"
    TRAEFIK = "proxy"


@dataclass
class ServerInfo:
    url: str
    operator: str
    environment_type: str
    active: bool


def fetch() -> List[ServerInfo]:
    try:
        log.info("Fetching metadata")
        resp = httpx.get(KNOWN_SERVERS_URL_METADATA)
        resp.raise_for_status()
    except HTTPError as ex:
        print("Can't fetch metadata", ex)
        sys.exit(1)

    try:
        metadata = resp.json()
    except JSONDecodeError as ex:
        print("Can't json parse metadata", ex)
        sys.exit(1)

    server_infos = []
    for env_type, url in KNOWN_SERVERS_URLS.items():
        try:
            log.info("Fetching known servers", env_type=env_type)
            resp = httpx.get(url)
            resp.raise_for_status()
        except HTTPError as ex:
            print(f"Can't load {env_type} servers", ex)
            sys.exit(1)

        try:
            server_list = resp.json()
        except JSONDecodeError as ex:
            print(f"Can't json decode {env_type} servers", ex)
            sys.exit(1)

        active_servers = server_list["active_servers"]
        all_servers = server_list["all_servers"]

        for server_url in all_servers:
            server_infos.append(
                ServerInfo(
                    url=server_url.removeprefix("transport."),
                    operator=metadata.get(server_url, {}).get("operator"),
                    environment_type=env_type,
                    active=(server_url in active_servers),
                )
            )
    log.info("Got servers", count=len(server_infos))
    return server_infos


def generate(target_path: Path, server_infos: List[ServerInfo]) -> None:
    log.info("Writing target files")
    for service in Services:
        target_file = target_path.joinpath(f"targets_rsb_{service.name.lower()}").with_suffix(
            ".json"
        )
        targets = []
        for server_info in server_infos:
            targets.append(
                {
                    "labels": {
                        "environment_type": server_info.environment_type,
                        "operator": server_info.operator,
                        "active": str(int(server_info.active)),
                    },
                    "targets": [f"{service.value}.{server_info.url}"],
                }
            )
        target_file.write_text(json.dumps(targets, indent=2))


@click.command()
@click.option(
    "--target-path",
    required=True,
    type=click_pathlib.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    default=Path.cwd(),
    show_default=True,
)
def main(target_path):
    generate(target_path, fetch())


if __name__ == "__main__":
    main()

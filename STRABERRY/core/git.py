import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO
    try:
        repo = Repo()
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
    except GitCommandError:
        LOGGER(__name__).info(f"Invalid Git Command")
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        origin.fetch()

        # Resolve the configured upstream branch safely.
        # Some repositories use 'main' while older ones use 'master'.
        branch = config.UPSTREAM_BRANCH
        remote_ref = None
        for candidate in (branch, "main", "master"):
            try:
                remote_ref = origin.refs[candidate]
                branch = candidate
                break
            except (IndexError, AttributeError):
                continue

        if remote_ref is None:
            available = [ref.name for ref in origin.refs]
            raise RuntimeError(
                f"Upstream branch '{config.UPSTREAM_BRANCH}' was not found. "
                f"Available origin refs: {available}"
            )

        if branch in repo.heads:
            repo.heads[branch].set_tracking_branch(remote_ref)
            repo.heads[branch].checkout(True)
        else:
            repo.create_head(branch, remote_ref)
            repo.heads[branch].set_tracking_branch(remote_ref)
            repo.heads[branch].checkout(True)
        try:
            repo.create_remote("origin", config.UPSTREAM_REPO)
        except BaseException:
            pass
        nrs = repo.remote("origin")
        # Fetch the branch that actually exists on the upstream remote.
        nrs.fetch(branch)
        try:
            nrs.pull(branch)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        install_req("pip3 install --no-cache-dir -r requirements.txt")
        LOGGER(__name__).info(f"Fetching updates from upstream repository...")

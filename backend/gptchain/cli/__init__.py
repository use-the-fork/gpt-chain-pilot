import asyncio
import os

import click
import nest_asyncio
import uvicorn

nest_asyncio.apply()

from gptchain.auth import ensure_jwt_secret
from gptchain.cache import init_lc_cache
from gptchain.cli.utils import check_file
from gptchain.config import (
    BACKEND_ROOT,
    DEFAULT_HOST,
    DEFAULT_PORT,
    config,
    init_config,
    load_module,
)
from gptchain.logger import logger
from gptchain.markdown import init_markdown
from gptchain.secret import random_secret
from gptchain.server import app, max_message_size, register_wildcard_route_handler
from gptchain.telemetry import trace_event


# Create the main command group for gptchain CLI
@click.group(context_settings={"auto_envvar_prefix": "gptchain"})
@click.version_option(prog_name="gptchain")
def cli():
    return


# Define the function to run gptchain with provided options
def run_gptchain(target: str):
    host = os.environ.get("gptchain_HOST", DEFAULT_HOST)
    port = int(os.environ.get("gptchain_PORT", DEFAULT_PORT))
    config.run.host = host
    config.run.port = port

    check_file(target)
    # Load the module provided by the user
    config.run.module_name = target
    load_module(config.run.module_name)

    ensure_jwt_secret()

    register_wildcard_route_handler()

    # Create the gptchain.md file if it doesn't exist
    init_markdown(config.root)

    # Initialize the LangChain cache if installed and enabled
    init_lc_cache()

    log_level = "debug" if config.run.debug else "error"

    # Start the server
    async def start():
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level=log_level,
            ws_max_size=max_message_size,
        )
        server = uvicorn.Server(config)
        await server.serve()

    # Run the asyncio event loop instead of uvloop to enable re entrance
    asyncio.run(start())
    # uvicorn.run(app, host=host, port=port, log_level=log_level)


# Define the "run" command for gptchain CLI
@cli.command("run")
@click.argument("target", required=True, envvar="RUN_TARGET")
@click.option(
    "-w",
    "--watch",
    default=False,
    is_flag=True,
    envvar="WATCH",
    help="Reload the app when the module changes",
)
@click.option(
    "-h",
    "--headless",
    default=False,
    is_flag=True,
    envvar="HEADLESS",
    help="Will prevent to auto open the app in the browser",
)
@click.option(
    "-d",
    "--debug",
    default=False,
    is_flag=True,
    envvar="DEBUG",
    help="Set the log level to debug",
)
@click.option(
    "-c",
    "--ci",
    default=False,
    is_flag=True,
    envvar="CI",
    help="Flag to run in CI mode",
)
@click.option(
    "--no-cache",
    default=False,
    is_flag=True,
    envvar="NO_CACHE",
    help="Useful to disable third parties cache, such as langchain.",
)
@click.option("--host", help="Specify a different host to run the server on")
@click.option("--port", help="Specify a different port to run the server on")
def gptchain_run(target, watch, headless, debug, ci, no_cache, host, port):
    if host:
        os.environ["gptchain_HOST"] = host
    if port:
        os.environ["gptchain_PORT"] = port
    if ci:
        logger.info("Running in CI mode")

        config.project.enable_telemetry = False
        no_cache = True
        # This is required to have OpenAI LLM providers available for the CI run
        os.environ["OPENAI_API_KEY"] = "sk-FAKE-OPENAI-API-KEY"
        # This is required for authenticationt tests
        os.environ["gptchain_AUTH_SECRET"] = "SUPER_SECRET"
    else:
        trace_event("gptchain run")

    config.run.headless = headless
    config.run.debug = debug
    config.run.no_cache = no_cache
    config.run.ci = ci
    config.run.watch = watch

    run_gptchain(target)


@cli.command("hello")
@click.argument("args", nargs=-1)
def gptchain_hello(args=None, **kwargs):
    trace_event("gptchain hello")
    hello_path = os.path.join(BACKEND_ROOT, "hello.py")
    run_gptchain(hello_path)


@cli.command("init")
@click.argument("args", nargs=-1)
def gptchain_init(args=None, **kwargs):
    trace_event("gptchain init")
    init_config(log=True)


@cli.command("create-secret")
@click.argument("args", nargs=-1)
def gptchain_create_secret(args=None, **kwargs):
    trace_event("gptchain secret")

    print(
        f"Copy the following secret into your .env file. Once it is set, changing it will logout all users with active sessions.\ngptchain_AUTH_SECRET={random_secret()}"
    )

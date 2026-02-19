import warnings

warnings.filterwarnings("ignore")  # Silence warnings in CLI

import os
import pathlib
import shutil
import subprocess

# Some imports are inline in CLI commands to keep initialization times low

import click

from serpent.utilities import (
    clear_terminal,
    display_serpent_logo,
    is_windows,
    is_linux,
)


# On Windows, disable the Fortran CTRL-C handler that gets installed with SciPy
if is_windows():
    os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "T"

VERSION = "2020.2.1"


@click.command(help="Perform Serpent.AI setup")
def setup():
    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI Setup")
    print("")

    data_path = _get_data_path()
    source_path = pathlib.Path(__file__).parent

    if data_path.exists():
        confirm = input(
            """It appears this machine has already been set up to use Serpent.AI.
Do you want to continue and remove all previous data? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

        print("")
        print("Removing previous data...")
        print("")

        shutil.rmtree(data_path, ignore_errors=True)

    print("Creating Serpent.AI data directory...")
    data_path.mkdir()

    print("Populating Serpent.AI data directory...")

    data_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    data_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    data_path.joinpath("game_agents").mkdir()

    # Copy config for framework (config.py, offshoot)
    data_path.joinpath("config").mkdir(exist_ok=True)
    shutil.copy(
        source_path.joinpath("serpent/config/config.yml"),
        data_path.joinpath("config/config.yml"),
    )
    shutil.copy(
        source_path.joinpath("serpent/config/config.plugins.yml"),
        data_path.joinpath("config/config.plugins.yml"),
    )
    shutil.copy(
        source_path.joinpath("serpent/offshoot.yml"),
        data_path.joinpath("offshoot.yml"),
    )
    shutil.copy(
        source_path.joinpath("serpent/offshoot.manifest.json"),
        data_path.joinpath("offshoot.manifest.json"),
    )
    shutil.copy(
        source_path.joinpath("serpent/crossbar.json"),
        data_path.joinpath("crossbar.json"),
    )
    shutil.copy(
        source_path.joinpath("serpent/config/config.json"),
        data_path.joinpath("config.json"),
    )

    # Copy bundled demo plugins (flat: plugins/SerpentXPlugin per offshoot)
    demo_game = source_path.joinpath("plugins", "SerpentDemoGamePlugin")
    demo_agent = source_path.joinpath("plugins", "SerpentDemoGameAgentPlugin")
    if demo_game.exists():
        shutil.copytree(demo_game, data_path.joinpath("plugins/SerpentDemoGamePlugin"), dirs_exist_ok=True)
    if demo_agent.exists():
        shutil.copytree(demo_agent, data_path.joinpath("plugins/SerpentDemoGameAgentPlugin"), dirs_exist_ok=True)

    print("")
    print("Serpent.AI Setup Complete!")


@click.command(help="Copy config to project root for local development")
def dev_setup():
    """Copy config files to project root so config.py finds them when running from repo."""
    source_path = pathlib.Path(__file__).parent
    current_path = pathlib.Path.cwd()

    config_dir = current_path.joinpath("config")
    config_dir.mkdir(exist_ok=True)

    shutil.copy(
        source_path.joinpath("serpent/config/config.yml"),
        config_dir.joinpath("config.yml"),
    )
    shutil.copy(
        source_path.joinpath("serpent/config/config.plugins.yml"),
        config_dir.joinpath("config.plugins.yml"),
    )

    # Copy offshoot files if not present
    for name in ("offshoot.yml", "offshoot.manifest.json"):
        src = source_path.joinpath(f"serpent/{name}")
        dst = current_path.joinpath(name)
        if not dst.exists():
            shutil.copy(src, dst)

    # Copy crossbar.json if not present
    crossbar_src = source_path.joinpath("serpent/crossbar.json")
    crossbar_dst = current_path.joinpath("crossbar.json")
    if not crossbar_dst.exists():
        shutil.copy(crossbar_src, crossbar_dst)

    print("Dev setup complete. Config copied to project root.")


@click.command(help="Update Serpent.AI to the latest version")
def update():
    import shlex

    clear_terminal()
    display_serpent_logo()
    print("")

    print("Updating Serpent.AI to the latest version...")
    print("")

    subprocess.call(shlex.split("pip install --upgrade SerpentAI"))

    # TODO: Handle files that were created with the setup commands
    #       and have likely been modified by the user. This is probably
    #       not an easy task.

    print("")
    print("Update Successful!")


@click.command(help="Launch the Serpent.AI GUI")
def gui():
    # TODO: Implement
    pass


@click.command(help="Download additional tools and modules")
@click.argument("module")
def download(module):
    valid_modules = ("tesseract",)

    if module not in valid_modules:
        print(f"'{module}' is not a valid download module...")
        return

    if module == "tesseract":
        if is_windows():
            print(f"Downloading module 'tesseract' to tools directory...")
            _download_module(
                "https://github.com/SerpentAI/SerpentAI/releases/download/optional/tesseract_4.00.00a_win_amd64.zip",
                pathlib.Path("tools/tesseract.zip"),
            )
        elif is_linux():
            print(
                "Downloading module 'tesseract' not supported on Linux. Please install Tesseract with your package manager."
            )


@click.command(help="Download and install a plugin from GitHub")
def download_plugin():
    # TODO: Implement
    pass


@click.command(help="Open the plugin directory")
def show_plugins():
    data_path = _get_data_path()
    plugins_path = data_path.joinpath("plugins")
    if not plugins_path.exists():
        print("Run 'serpent setup' first.")
        return
    if is_windows():
        os.startfile(str(plugins_path))
    else:
        subprocess.run(["xdg-open", str(plugins_path)], check=False)


@click.command(help="List all installed plugins")
def plugins():
    data_path = _get_data_path()
    plugins_path = data_path.joinpath("plugins")
    if not plugins_path.exists():
        print("Run 'serpent setup' first.")
        return
    for kind in ("games", "game_agents", "rl_agents"):
        path = plugins_path.joinpath(kind)
        if path.exists():
            items = [d.name for d in path.iterdir() if d.is_dir()]
            print(f"\n{kind.replace('_', ' ').title()}:")
            print("\n".join(items) if items else "  (none)")


@click.command(help="List the installed game plugins")
def games():
    _list_plugins("games")


@click.command(help="List the installed game agent plugins")
def game_agents():
    _list_plugins("game_agents")


@click.command(help="List the installed reinforcement learning agent plugins")
def rl_agents():
    _list_plugins("rl_agents")


def _list_plugins(kind: str):
    data_path = _get_data_path()
    plugins_root = data_path.joinpath("plugins")
    if not plugins_root.exists():
        print("Run 'serpent setup' first.")
        return
    items = []
    category_path = plugins_root.joinpath(kind)
    if category_path.exists():
        items.extend(d.name for d in category_path.iterdir() if d.is_dir())
    suffix = "GamePlugin" if kind == "games" else "GameAgentPlugin" if kind == "game_agents" else "RLAgentPlugin"
    for d in plugins_root.iterdir():
        if d.is_dir() and d.name.endswith(suffix) and d.name not in items:
            items.append(d.name)
    # For display: "SerpentDemoGamePlugin" -> "Demo"
    if kind == "games":
        items = [n.replace("Serpent", "").replace("GamePlugin", "") for n in items]
    elif kind == "game_agents":
        items = [n.replace("Serpent", "").replace("GameAgentPlugin", "") for n in items]
    print("\n".join(items) if items else "(none)")


@click.command(help="Display instructions from a game plugin")
@click.argument("game_name")
def game_instructions(game_name):
    print(f"Instructions for {game_name}: See the game plugin's README or wiki.")


@click.command(help="Launch a game")
@click.argument("game_name")
def launch(game_name):
    _run_from_data_path("launch", game_name)


@click.command(help="Train a game agent")
@click.argument("training_type")
@click.argument("args", nargs=-1)
def train(training_type, args):
    _run_from_data_path("train", training_type, *args)


@click.command(help="Play a game using a game agent")
@click.argument("game_name")
@click.argument("game_agent_name")
@click.option("--frame-handler", default=None, help="Frame handler to use")
def play(game_name, game_agent_name, frame_handler):
    args = [game_name, game_agent_name]
    if frame_handler:
        args.append(frame_handler)
    _run_from_data_path("play", *args)


@click.command(help="Record inputs while playing a game")
@click.argument("game_name")
@click.argument("game_agent_name")
@click.option("--frame-count", default=4, help="Frame count")
@click.option("--frame-spacing", default=4, help="Frame spacing")
def record(game_name, game_agent_name, frame_count, frame_spacing):
    _run_from_data_path("record", game_name, game_agent_name, str(frame_count), str(frame_spacing))


def _run_from_data_path(command: str, *args):
    data_path = _get_data_path()
    if not data_path.exists():
        print("Run 'serpent setup' first.")
        return
    config_dir = data_path.joinpath("config")
    if not config_dir.exists() or not config_dir.joinpath("config.yml").exists():
        print("Data directory incomplete. Run 'serpent setup' again.")
        return
    orig_cwd = os.getcwd()
    try:
        os.chdir(data_path)
        import serpent.serpent as legacy
        fn = getattr(legacy, command, None)
        if fn is None:
            print(f"Command '{command}' not available.")
            return
        fn(*args)
    finally:
        os.chdir(orig_cwd)


# SDK
# These commands are aimed at developers wanting to create plugins for Serpent.AI
@click.command(help="SDK - Perform Serpent.AI SDK setup in the current directory")
def sdk_setup():
    import serpent.ocr

    clear_terminal()
    display_serpent_logo()

    print("")
    print("Serpent.AI SDK Setup")
    print("")

    # First, check for required 3rd-party tools
    print("Checking for required 3rd-party tools...")

    have_tesseract = serpent.ocr.is_tesseract_available()

    print(f"Tesseract: {'FOUND' if have_tesseract else 'NOT FOUND'}")
    print("")

    if not have_tesseract:
        print("No Tesseract executable could be found... Setup cannot continue.")
        print("")

        if is_windows():
            print(
                "For an easy installation of Tesseract, run 'serpent download tesseract"
            )

    # Has setup already been performed?
    if pathlib.Path(".serpent-sdk").is_file():
        confirm = input(
            """The current directory has already been set up to use the Serpent.AI SDK.
Do you want to continue and potentially overwrite important files? 
(One of: 'YES', 'NO') """
        )

        if confirm.lower() != "yes":
            return

    current_path = pathlib.Path.cwd()
    source_path = pathlib.Path(__file__).parent

    # Config
    config_path = pathlib.Path("config_sdk.json")

    if config_path.is_file():
        config_path.unlink()

    shutil.copy(source_path.joinpath("serpent/config/config_sdk.json"), config_path)

    # Plugins
    plugins_path = current_path.joinpath("plugins")

    if plugins_path.is_dir():
        shutil.rmtree(plugins_path, ignore_errors=True)

    current_path.joinpath("plugins/games").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/game_agents").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("plugins/rl_agents").mkdir(parents=True, exist_ok=True)

    # Config (for config.py when running from this directory)
    current_path.joinpath("config").mkdir(exist_ok=True)
    shutil.copy(source_path.joinpath("serpent/config/config.yml"), current_path.joinpath("config/config.yml"))
    shutil.copy(source_path.joinpath("serpent/config/config.plugins.yml"), current_path.joinpath("config/config.plugins.yml"))
    shutil.copy(source_path.joinpath("serpent/offshoot.yml"), current_path.joinpath("offshoot.yml"))
    shutil.copy(source_path.joinpath("serpent/offshoot.manifest.json"), current_path.joinpath("offshoot.manifest.json"))
    shutil.copy(source_path.joinpath("serpent/crossbar.json"), current_path.joinpath("crossbar.json"))

    # Datasets
    datasets_path = current_path.joinpath("datasets")

    if datasets_path.is_dir():
        shutil.rmtree(datasets_path, ignore_errors=True)

    current_path.joinpath("datasets/frames").mkdir(parents=True, exist_ok=True)
    current_path.joinpath("datasets/recordings").mkdir(parents=True, exist_ok=True)

    # Dot File
    open(".serpent-sdk", "w").close()

    print("")
    print("Serpent.AI SDK Setup Complete!")


@click.command(help="SDK - Find the window name of a game")
def sdk_window_name():
    _ensure_sdk_config()
    from serpent.utilities import clear_terminal, display_serpent_logo
    import time
    from serpent.window_controller import WindowController

    clear_terminal()
    display_serpent_logo()
    print("")
    print("Open the game manually.")
    input("\nPress Enter and then focus the game window...")
    window_controller = WindowController()
    time.sleep(5)
    focused_window_name = window_controller.get_focused_window_name()
    print("\nGame Window Detected! Set kwargs['window_name'] in the game plugin to:")
    print("\n" + focused_window_name + "\n")


def _ensure_sdk_config():
    """Ensure config exists in cwd for SDK commands."""
    config_yml = pathlib.Path("config/config.yml")
    if not config_yml.exists():
        source = pathlib.Path(__file__).parent
        pathlib.Path("config").mkdir(exist_ok=True)
        shutil.copy(source.joinpath("serpent/config/config.yml"), "config/config.yml")
        shutil.copy(source.joinpath("serpent/config/config.plugins.yml"), "config/config.plugins.yml")
        if not pathlib.Path("offshoot.yml").exists():
            shutil.copy(source.joinpath("serpent/offshoot.yml"), "offshoot.yml")
        if not pathlib.Path("offshoot.manifest.json").exists():
            shutil.copy(source.joinpath("serpent/offshoot.manifest.json"), "offshoot.manifest.json")


@click.command(help="SDK - CUDA test for Serpent.AI")
def sdk_test_cuda():
    import torch

    # TODO: Try to also detect incompatible hardware. This likely just detects if CUDA
    #       is bundled with the installed PyTorch version
    if torch.cuda.is_available():
        print("Success! CUDA can be used by Serpent.AI")
    else:
        print("Failure! CUDA cannot be used by Serpent.AI")


@click.command(help="SDK - Test Serpent.AI input capture")
def sdk_test_input_capture():
    # TODO: Implement
    pass


@click.command(help="SDK - Capture game frames")
@click.option("--width", default=640, help="Frame width")
@click.option("--height", default=480, help="Frame height")
@click.option("--x-offset", default=0, help="X offset")
@click.option("--y-offset", default=0, help="Y offset")
def sdk_capture(width, height, x_offset, y_offset):
    _ensure_sdk_config()
    from serpent.frame_grabber import FrameGrabber

    print("Starting frame grabber. Press Ctrl+C to stop.")
    frame_grabber = FrameGrabber(
        width=int(width),
        height=int(height),
        x_offset=int(x_offset),
        y_offset=int(y_offset),
    )
    frame_grabber.start()


@click.command(help="SDK - Generate skeleton for a game plugin")
@click.argument("game_name", required=False)
@click.option("--platform", type=click.Choice(["steam", "executable", "web_browser"]), default="executable")
def sdk_generate_game_plugin(game_name, platform):
    _ensure_sdk_config()
    if not game_name:
        game_name = click.prompt("Game name (Titleized, no spaces, e.g. AwesomeGame)")
    _copy_game_plugin_template(game_name, platform)


def _copy_game_plugin_template(game_name: str, platform: str):
    """Copy game plugin template and do basic substitution."""
    source_path = pathlib.Path(__file__).parent
    template = source_path.joinpath("serpent/templates/SerpentGamePlugin")
    dest = pathlib.Path.cwd().joinpath("plugins", f"Serpent{game_name}GamePlugin")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"Plugin already exists: {dest}")
        return
    shutil.copytree(template, dest)
    plugin_py = dest.joinpath("plugin.py")
    plugin_py.write_text(plugin_py.read_text().replace("SerpentGamePlugin", f"Serpent{game_name}GamePlugin"))
    game_file = dest.joinpath("files/serpent_game.py")
    new_name = f"serpent_{game_name.lower()}_game.py"
    game_file.rename(dest.joinpath("files", new_name))
    content = dest.joinpath("files", new_name).read_text()
    content = content.replace("SerpentGame", f"Serpent{game_name}Game").replace("MyGameAPI", f"{game_name}API")
    dest.joinpath("files", new_name).write_text(content)
    api_py = dest.joinpath("files/api/api.py")
    api_py.write_text(api_py.read_text().replace("MyGameAPI", f"{game_name}API"))
    print(f"Created game plugin: {dest}")


@click.command(help="SDK - Generate skeleton for a game agent plugin")
@click.argument("game_agent_name", required=False)
def sdk_generate_game_agent_plugin(game_agent_name):
    _ensure_sdk_config()
    if not game_agent_name:
        game_agent_name = click.prompt("Game agent name (Titleized, no spaces, e.g. AwesomeGameAgent)")
    source_path = pathlib.Path(__file__).parent
    plugins_path = pathlib.Path.cwd().joinpath("plugins")
    plugins_path.mkdir(parents=True, exist_ok=True)
    template = source_path.joinpath("serpent/templates/SerpentGameAgentPlugin")
    dest = plugins_path.joinpath(f"Serpent{game_agent_name}GameAgentPlugin")
    if dest.exists():
        print(f"Plugin already exists: {dest}")
        return
    shutil.copytree(template, dest)
    agent_file = dest.joinpath("files/serpent_game_agent.py")
    new_agent_name = f"serpent_{game_agent_name.lower().replace(' ', '')}_game_agent.py"
    agent_file.rename(dest.joinpath("files", new_agent_name))
    for f in [dest.joinpath("plugin.py"), dest.joinpath("files", new_agent_name)]:
        content = f.read_text()
        content = content.replace("SerpentGameAgentPlugin", f"Serpent{game_agent_name}GameAgentPlugin")
        content = content.replace("SerpentGameAgent", f"Serpent{game_agent_name}GameAgent")
        content = content.replace("serpent_game_agent.py", new_agent_name)
        f.write_text(content)
    print(f"Created game agent plugin: {dest}")


@click.command(help="SDK - Generate skeleton for a RL agent plugin")
def sdk_generate_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game plugin to .spg file")
def sdk_package_game_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package game agent plugin to .spga file")
def sdk_package_game_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Package RL agent plugin to .sprla file")
def sdk_package_rl_agent_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Install a plugin on the system")
def sdk_install_plugin():
    # TODO: Implement
    pass


@click.command(help="SDK - Uninstall a plugin from the system")
def sdk_uninstall_plugin():
    # TODO: Implement
    pass


def _download_module(url, file_path):
    import requests
    import tqdm

    path = file_path.parent
    path.mkdir(parents=True, exist_ok=True)

    r = requests.get(url, stream=True)

    with open(file_path, "wb") as f:
        progress = tqdm.tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=int(r.headers["Content-Length"]),
        )

        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                progress.update(len(chunk))
                f.write(chunk)

        progress.close()

    if str(file_path.as_posix()).endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(file_path, "r") as z:
            z.extractall(path)

        file_path.unlink()

    print("Download complete!")


def _get_data_path():
    if is_windows():
        data_path = pathlib.Path(os.getenv("APPDATA")).joinpath("Serpent.AI")
    elif is_linux():
        data_path = pathlib.Path(os.getenv("HOME")).joinpath(".serpent")

    return data_path.absolute()


@click.group(invoke_without_command=True)
@click.option("--version", help="Shows Serpent.AI version", is_flag=True)
@click.option("--help", help="Shows Serpent.AI CLI commands", is_flag=True)
@click.pass_context
def cli(context, version, help):
    if version:
        print(VERSION)
        return

    if context.invoked_subcommand is None:
        print(context.get_help())
        return


# General
cli.add_command(setup)
cli.add_command(dev_setup)
cli.add_command(update)
cli.add_command(gui)
cli.add_command(download)
cli.add_command(show_plugins)
cli.add_command(plugins)
cli.add_command(games)
cli.add_command(game_agents)
cli.add_command(rl_agents)
cli.add_command(game_instructions)
cli.add_command(launch)
cli.add_command(train)
cli.add_command(play)
cli.add_command(record)

# SDK
cli.add_command(sdk_setup)
cli.add_command(sdk_window_name)
cli.add_command(sdk_test_cuda)
cli.add_command(sdk_test_input_capture)
cli.add_command(sdk_capture)
cli.add_command(sdk_generate_game_plugin)
cli.add_command(sdk_generate_game_agent_plugin)
cli.add_command(sdk_generate_rl_agent_plugin)
cli.add_command(sdk_package_game_plugin)
cli.add_command(sdk_package_game_agent_plugin)
cli.add_command(sdk_package_rl_agent_plugin)
cli.add_command(sdk_install_plugin)
cli.add_command(sdk_uninstall_plugin)


if __name__ == "__main__":
    cli()

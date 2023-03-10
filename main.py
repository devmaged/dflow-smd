import concurrent.futures
import time
import requests
import rich
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
from app.app import SnapchatScrapper
from app.helpers import NoStoriesFound, clear, banner, APIResponseError, UserNotFoundError
import git


def main():
    clear()
    print(banner())

    """
    To automatically pull the code from repo
    """
    rich.print(f"[[yellow bold]*[/]] Updating the tool ...")
    try:
        g = git.cmd.Git('./')
        g.pull()
        rich.print(f"[[green bold]✔[/]] The tool is up to date.")
    except (Exception,):
        rich.print(f"[[red bold]![/]] Failed to update the tool.")

    """
    Try to fetch users list from API then save them if, if failed, Try to fetch it locally from users.txt    
    """
    rich.print(f"[[yellow bold]*[/]] Fetching users list from API ...")
    try:
        res = requests.get('https://dashboard.dflow.tech/api/acl/influencer/hander')
        users_list = res.json()['data']
        rich.print(f"[[green bold]✔[/]] Fetched a total of {len(users_list)} users.")

        with open('users.txt', 'w') as file:
            file.write('\n'.join(users_list))
        file.close()

    except (Exception,):
        rich.print(f"[[red bold]![/]] Failed to Fetch users list from API.")
        rich.print(f"[[yellow bold]*[/]] Fetching users list from users.text file ...")
        try:
            f = open('users.txt', "r")
            data = f.read()
            users_list = data.split("\n")
            rich.print(f"[[green bold]✔[/]] Fetched a total of {len(users_list)} users.")
            f.close()
        except (Exception,):
            rich.print(f"[[red bold]![/]] Failed to Fetch users list locally.")
            rich.print(f"[[red bold]![/]] Quitting ...\n")
            exit()

    sc = SnapchatScrapper()

    text_column = TextColumn("Finished {task.completed} out of {task.total}")
    bar_column = BarColumn()
    progress = Progress(
        text_column,
        bar_column,
        TimeRemainingColumn(),
        TimeElapsedColumn(),
    )

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    with progress as progress:
        try:
            for user in progress.track(users_list):
                try:
                    sc.download(user, executor)

                except NoStoriesFound:
                    rich.print(f"[[red bold]![/]] User '{user}' has no stories ...")
                except APIResponseError:
                    rich.print(f"[[red bold]![/]] User '{user}' is not public ...")
                except UserNotFoundError:
                    rich.print(f"[[red bold]![/]] User '{user}' is not found ...")

        except KeyboardInterrupt:
            rich.print(f"[[red bold]![/]] Quitting, please wait ...\n")
        except (Exception,):
            rich.print(f"[[red bold]![/]] An error occurred, quitting ...\n")
        finally:
            executor.shutdown(wait=True)

        rich.print(f"\n[[green bold]![/]] Downloaded a total of {sc.total} stories ...")
        exit()


if __name__ == "__main__":
    main()

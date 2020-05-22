import os
import click
import git
import coloredlogs
import logging
import tempfile
from simple_term_menu import TerminalMenu


logger = logging.getLogger("main")


def print_error(msg):
    click.echo(click.style(msg, fg="red"))


def setup_logging(debug):
    if debug:
        coloredlogs.install(level="DEBUG")
    else:
        coloredlogs.install(level="INFO")


def build_rebase_script(repo, sha):
    lines = [f"edit {sha}"]
    for commit in repo.iter_commits(f"{sha}..HEAD", reverse=True):
        lines.append(f"pick {str(commit)}")
    return "\n".join(lines)


def show_menu(options, title):
    selected_options = set()
    while True:
        all_options = []
        for idx, opt in enumerate(options):
            if idx in selected_options:
                prefix = "[*]"
            else:
                prefix = "[ ]"
            all_options.append(f'{prefix} {opt["option_name"]}')
        all_options.append("❌ Cancel")
        all_options.append("✅ Done")

        menu = TerminalMenu(all_options, title=title)
        idx = menu.show()
        if idx < len(options):
            if idx in selected_options:
                selected_options.remove(idx)
            else:
                selected_options.add(idx)
        elif idx == len(options):
            return None
        else:
            return [options[idx]["file_diff"] for idx in selected_options]


def pick_the_split(repo, base_sha):
    """Interactively split the operations in `base_sha` into two lists of operations.
    
    This method is non-destructive.
    """
    previous_commit = repo.commit(f"{base_sha}~1")
    all_operations = previous_commit.diff(base_sha)
    options = []
    for d in all_operations:
        option_name = f"{d.change_type}  {d.a_path}"
        option = {
            "option_name": option_name,
            "file_diff": d,
        }
        options.append(option)

    click.echo("")
    first_diffs = show_menu(options, title="Select operations to keep in first commit")
    if first_diffs is None:
        raise click.Abort()
    elif not first_diffs:
        print_error(f"Error: Must select at least one operation for first commit.")
        raise click.Abort()
    elif len(first_diffs) == len(options):
        print_error(f"Error: Must leave at least one operation for second commit.")
        raise click.Abort()

    second_diffs = set(all_operations).symmetric_difference(first_diffs)
    return first_diffs, second_diffs


def review_split(first_diffs, second_diffs):
    """Prompts the user to review and confirm a split.

    This method is non-destructive.
    """
    click.echo("Ready to split! Please review:")
    click.echo("")

    for name, diffs in (("First", first_diffs), ("Second", second_diffs)):
        click.echo(f"{name} commit:")
        click.echo("")
        for d in diffs:
            click.echo(f"  {d.change_type} {d.a_path}")
        click.echo()

    proceed = click.confirm("Proceed?")
    if not proceed:
        raise click.Abort()


def execute_split(
    output_branch_name, repo, source_commit, first_diffs, second_diffs, second_commit_message
):
    """Executes the split. This method is destructive!"""
    base_sha = str(source_commit)
    logging.debug(f'Creating branch "{output_branch_name}" at HEAD')
    branch_head = repo.create_head(output_branch_name)

    logging.debug(f"Switching into branch")
    repo.head.reference = branch_head
    assert not repo.head.is_detached
    repo.head.reset(index=True, working_tree=True)

    script = build_rebase_script(repo, base_sha)
    logger.debug(f"rebase script:\n{script}")

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    logger.debug(f"Writing rebase script to {temp_file.name}")
    temp_file.write(script.encode())
    temp_file.close()

    first_commit_message_file = tempfile.NamedTemporaryFile(delete=False)
    logger.debug(f"Writing commit message to {first_commit_message_file.name}")
    first_commit_message_file.write(str(source_commit.message).encode())
    first_commit_message_file.close()

    # Faking an interactive rebase requires overriding `GIT_SEQUENCE_EDITOR`,
    # so we do that here.
    #
    # NOTE(mikey): We're creating the rebase script on our own, and
    # feeding it directly to `git rebase -i`. We could alternatively read
    # the default rebase script, and edit the first line. This might be
    # safer, our implementation of `build_rebase_script()` could be buggy.
    custom_env = {
        "GIT_SEQUENCE_EDITOR": f"cat '{temp_file.name}' >",
    }

    repo_git = repo.git
    with repo_git.custom_environment(**custom_env):
        repo_git.rebase("-i", f"{base_sha}^")
        repo_git.reset("HEAD^")
        for d in first_diffs:
            stage_diff(repo_git, d)
        repo_git.commit("-F", first_commit_message_file.name)
        for d in second_diffs:
            stage_diff(repo_git, d)
        repo_git.commit("-m", second_commit_message)
        repo_git.rebase("--continue")


def stage_diff(repo_git, diff):
    """Given a diff object, run `git add` or `git rm` for it within `repo_git`."""
    if diff.change_type == "A":
        repo_git.add(diff.a_path)
    elif diff.change_type == "D":
        repo_git.rm(diff.a_path)
    else:
        repo_git.add("-u", diff.a_path)


@click.command()
@click.argument("sha")
@click.option("--debug/--no-debug", default=False)
@click.option("--output_branch_name", default="split-commit-tmp", prompt=True)
def split(sha, debug, output_branch_name):
    setup_logging(debug)
    repo = git.Repo(search_parent_directories=True)
    logger.debug(f"Initialized repo: {repo.working_tree_dir}")

    try:
        commit = repo.commit(sha)
    except git.exc.BadName:
        print_error(f"Error: Commit {sha} not found")
        raise click.Abort()

    try:
        existing_branch = repo.commit(output_branch_name)
    except git.exc.BadName:
        pass
    else:
        print_error(f"Error: The branch {output_branch_name} already exists")
        raise click.Abort()

    base_sha = str(commit)
    first_diffs, second_diffs = pick_the_split(repo, base_sha)
    second_commit_message = click.prompt(
        "Message for second commit?", default="Split from previous commit"
    )

    review_split(first_diffs, second_diffs)
    execute_split(
        output_branch_name, repo, commit, first_diffs, second_diffs, second_commit_message
    )
    click.echo("🍌 Split complete! Enjoy your day.")

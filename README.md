# git-split-commit

Did you goof and make a single git commit that should have been two sequential
commits?

Tired of trying to remember the sequence of rebase steps you _know_ can
fix this, but always have to drag yer ass over to StackOverflow to look up again?

`git split-commit` is for you!

> **🚨Warning:** This is experimental and is definitely buggy. Always backup before using and verify results.

![render1590174050770](https://user-images.githubusercontent.com/390829/82701274-dcd36100-9c3d-11ea-8bb2-7e54edb2155d.gif)


## Usage

```
$ git split-commit <sha-to-split>
```


## Installation

Requires [pipx](https://github.com/pipxproject/pipx) to install.

```
$ pip install pipx
$ pipx install git+https://github.com/mik3y/git-split-commit.git
```


## Example

Let's look at [a simple project](https://github.com/mik3y/git-split-commit-example-repo). After a splendid day of hacking, our repo has a
handful of files:

```
$ git clone git@github.com:mik3y/git-split-commit-example-repo.git example
$ cd example
$ ls -R
README.md pages

./pages:
account.html   index.html   privacy.html
```

Here's the commit history for the day:

```
$ git lg
* e0609c2 - (HEAD -> master, origin/master, origin/HEAD) Update README.md (2 hours ago) <mike wakerly>
* 72774ad - Add account.html (2 hours ago) <mike wakerly>
* c4f0f07 - Initial project. (2 hours ago) <mike wakerly>
```

Oh no! Our commit history is not what we expected: We meant to add
`account.html` and `privacy.html` in two different commits, but we accidentally
did them all in one commit.

While the end state of the project is right, we really wanted to have nice
easy-to-understand "single purpose" commits in our history. Maybe this is because we
want the history to be easier for others to read and follow. In any case, how do
we break up `0eb6011` into 2 sequential commits?

Let's use `git split-commit`!

```
$ git split-commit 72774ad
Output branch name [split-commit-tmp]:

Message for second commit? [Split from previous commit]: Add privacy.html
Ready to split! Please review:

First commit:

  A pages/account.html
  A pages/index.html

Second commit:

  A pages/privacy.html

Proceed? [y/N]: y
🍌 Split complete! Enjoy your day.
```

Success! Check out our new history:

```
$ git lg
* 43525f8 - (HEAD -> split-commit-tmp) Update README.md (14 seconds ago) <mike wakerly>
* b7890cc - Add privacy.html (14 seconds ago) <mike wakerly>
* 6e50068 - Add account.html (15 seconds ago) <mike wakerly>
* c4f0f07 - Initial project. (2 hours ago) <mike wakerly>
```

## TODO

* Test things - a lot.
* Figure out how to handle root commits.
* Fix up cursor jumping in select menu.
* Consider using `pygit2` bindings.

## Changelog

* v0.1.0 (2020-05-22) - Initial version. Sorta works.

## License

`git-split-commit` is licensed under the MIT License. We hope you do wonderful things with it.
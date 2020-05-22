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

```
$ pipx install git-split-commit
```


## Example

Let's look at a simple project. After a splendid day of hacking, our repo has a
handful of files:

```
$ ls
README.md
index.html
pages/account.html
pages/privacy.html
```

Here's the commit history for the day:

```
$ git lg
* 27a76c6 - (HEAD -> master) Update docs (2 minutes ago) <Mary Maker>
* 0eb6011 - Add account.html (3 hours ago) <Mary Maker>
* 8c79d74 - Initial project (9 hours ago) <Mary Maker>
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
$ git split-commit 0eb6011
Will break commit 0eb6011 into two different commits.

Select files for first commit:
[*] pages/account.html
[ ] pages/privacy.html

[Continue] (Abort)

Committed first commit. New SHA: 82ef311

Files automatically selected for second commit:
+ pages/privacy.html

Press enter to edit commit message in your editor.

Committed second commit. New SHA: b402f9e
Finishing rebase...

Done! Thanks for a great split.
```

Success! Check out our new history:

```
$ git lg
* 7ec1c09 - (HEAD -> master) Update docs (1 minute ago) <Mary Maker>
* b402f9e - Add privacy.html (1 minute ago) <Mary Maker>
* 82ef311 - Add account.html (3 hours ago) <Mary Maker>
* 8c79d74 - Initial project (9 hours ago) <Mary Maker>
```

## Changelog

* v0.1.0 (2020-05-22) - Initial version. Works

## License

`git-split-commit` is licensed under the MIT License. We hope you do wonderful things with it.
clean:
	rm -rf *.egg-info

format:
	black git_split_commit/

.PHONY: clean format


import git

# Clone a repository
git.Git().clone("https://github.com/sindhuA1501/deviceOffline")

# Open an existing repository
repo = git.Repo("/home/pi/Downloads/Schduletest")

# Pull the latest changes from the remote
repo.remotes.origin.pull()

# Make sure that we have the last version of the repo
echo "Updating repo..."
git pull

# Create a virtualenv
echo "Creating virtualenv..."
virtualenv Env

# Install local package
(source Env/bin/activate && pip install -r requirements && pip install -e Src/)
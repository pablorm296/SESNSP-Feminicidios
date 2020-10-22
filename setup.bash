
# Make sure that we have the last version of the repo
echo "Updating repo..."
git pull

# Create a virtualenv
echo "Creating virtualenv..."
virtualenv Env

# Activate virtualenv
source Env/bin/activate

# Install requirements
pip install -r requirements.txt

# Install local package
pip install -e Src/
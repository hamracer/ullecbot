apt-get update
apt-get install python3-pip
pip install -r requirements.txt

git config --global user.email "totallynotcellu@gmail.com"
git config --global user.name "Cellu"

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
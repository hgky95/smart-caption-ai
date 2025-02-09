cd /home/ubuntu/python_project/smart-caption-ai || exit

echo "Pulling latest code..."
git pull https://github.com/hgky95/smart-caption-ai.git main

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt


echo "Restarting service..."
sudo systemctl restart smartcaption_ai.service

echo "Deployment complete"
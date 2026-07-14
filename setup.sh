#!/bin/bash

echo "🚀 Setting up BMI & Fitness Toolkit..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "📝 To run the app:"
echo "   streamlit run app.py"
echo ""
echo "📤 To deploy to GitHub:"
echo "   git init"
echo "   git add ."
echo '   git commit -m "Initial commit"'
echo "   git remote add origin https://github.com/YOUR_USERNAME/fitness-bmi-tracker.git"
echo "   git push -u origin main"
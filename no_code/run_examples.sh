#!/bin/bash

echo "Starting Wave Visualizer Examples..."
echo

# Check if conda is available
echo "[STEP 1/6] Checking for conda installation..."
echo "Searching for conda in common locations..."

# Method 1: Check if conda is in PATH
if command -v conda &> /dev/null; then
    echo "SUCCESS: Found conda in PATH!"
    CONDA_FOUND=true
else
    CONDA_FOUND=false
    echo "Conda not found in PATH, checking default locations..."
    
    # Method 2: Try common conda installation paths
    CONDA_PATHS=(
        "$HOME/anaconda3/bin/conda"
        "$HOME/miniconda3/bin/conda"
        "/opt/anaconda3/bin/conda"
        "/opt/miniconda3/bin/conda"
        "/usr/local/anaconda3/bin/conda"
        "/usr/local/miniconda3/bin/conda"
        "$HOME/opt/anaconda3/bin/conda"
        "$HOME/opt/miniconda3/bin/conda"
    )
    
    for conda_path in "${CONDA_PATHS[@]}"; do
        if [ -f "$conda_path" ]; then
            echo "Found conda at: $conda_path"
            export PATH="$(dirname "$conda_path"):$PATH"
            CONDA_FOUND=true
            break
        fi
    done
fi

if [ "$CONDA_FOUND" = false ]; then
    echo
    echo "========================================================"
    echo "ERROR: Conda not found on your system!"
    echo "========================================================"
    echo
    echo "We searched these locations:"
    echo "1. System PATH"
    echo "2. $HOME/anaconda3/bin/"
    echo "3. $HOME/miniconda3/bin/"
    echo "4. /opt/anaconda3/bin/"
    echo "5. /opt/miniconda3/bin/"
    echo "6. /usr/local/anaconda3/bin/"
    echo "7. /usr/local/miniconda3/bin/"
    echo "8. $HOME/opt/anaconda3/bin/"
    echo "9. $HOME/opt/miniconda3/bin/"
    echo
    echo "SOLUTION: Install conda first, then try again"
    echo
    echo "OPTION 1 - Anaconda (Recommended for beginners):"
    echo "  Download: https://www.anaconda.com/products/distribution"
    echo "  Follow installation instructions for your OS"
    echo
    echo "OPTION 2 - Miniconda (Minimal installation):"
    echo "  Download: https://docs.conda.io/en/latest/miniconda.html"
    echo "  Choose the installer for your operating system"
    echo
    echo "After installation:"
    echo "  1. Restart your terminal (or run: source ~/.bashrc)"
    echo "  2. Run this script again"
    echo
    echo "Current PATH: $PATH"
    echo
    read -p "Press any key to exit..."
    exit 1
fi

echo "SUCCESS: Conda found and configured!"

# Initialize conda for bash
echo "[STEP 2/6] Initializing conda for bash..."

# Try to source conda from common locations if not already available
if ! type conda > /dev/null 2>&1; then
    echo "Conda command not available, sourcing conda initialization..."
    CONDA_INIT_PATHS=(
        "$HOME/anaconda3/etc/profile.d/conda.sh"
        "$HOME/miniconda3/etc/profile.d/conda.sh"
        "/opt/anaconda3/etc/profile.d/conda.sh"
        "/opt/miniconda3/etc/profile.d/conda.sh"
        "/usr/local/anaconda3/etc/profile.d/conda.sh"
        "/usr/local/miniconda3/etc/profile.d/conda.sh"
    )
    
    for init_path in "${CONDA_INIT_PATHS[@]}"; do
        if [ -f "$init_path" ]; then
            echo "Sourcing conda from: $init_path"
            source "$init_path"
            break
        fi
    done
fi

# Initialize conda hook
eval "$(conda shell.bash hook)" 2>/dev/null || {
    echo "ERROR: Could not initialize conda for bash."
    echo "Please try running: conda init bash"
    echo "Then restart your terminal and try again."
    read -p "Press any key to exit..."
    exit 1
}

echo "SUCCESS: Conda initialized for bash!"

# Check if goldman_env environment exists
echo "[STEP 3/6] Checking for goldman_env environment..."
if ! conda info --envs | grep -q "goldman_env"; then
    echo "WARNING: goldman_env environment not found."
    echo "Creating environment from environment.yml..."
    echo
    
    # Navigate to parent directory where environment.yml should be
    cd ..
    echo "Current directory: $(pwd)"
    
    # Check if environment.yml exists
    if [ ! -f "environment.yml" ]; then
        echo "ERROR: environment.yml not found in project directory."
        echo "Expected location: $(pwd)/environment.yml"
        echo "Make sure you're running this from the correct no_code folder."
        echo
        echo "Directory contents:"
        ls -la
        echo
        read -p "Press any key to exit..."
        exit 1
    fi
    
    # Create the environment
    echo "Creating conda environment... This may take a few minutes."
    echo "Please wait..."
    conda env create -f environment.yml
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create conda environment."
        echo "Please check that environment.yml is valid and try again."
        read -p "Press any key to exit..."
        exit 1
    fi
    
    echo "SUCCESS: goldman_env environment created!"
    echo
    
    # Go back to no_code directory
    cd no_code
else
    echo "SUCCESS: goldman_env environment found!"
fi

# Activate the goldman_env environment
echo "[STEP 4/6] Activating goldman_env conda environment..."
conda activate goldman_env
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate goldman_env environment."
    echo
    echo "Please try these manual steps:"
    echo "1. Open a new terminal"
    echo "2. Run: conda activate goldman_env"
    echo "3. Run: python example_visualizations/political_w1_w3.py"
    echo
    read -p "Press any key to exit..."
    exit 1
fi

echo "SUCCESS: goldman_env environment activated!"

# Navigate to project root first (where pyproject.toml is located)
cd ..

# Install the wave_visualizer package in editable mode
echo "[STEP 5/7] Installing wave_visualizer package..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "WARNING: Failed to install wave_visualizer package."
    echo "This might cause import errors in the examples."
    echo
else
    echo "SUCCESS: wave_visualizer package installed!"
fi

# We're already in project root now
echo "[STEP 6/7] Checking project directory..."

# Check if example_visualizations exists
if [ ! -d "example_visualizations" ]; then
    echo "ERROR: example_visualizations folder not found."
    echo "Current directory: $(pwd)"
    echo "Make sure you're running this from the correct location."
    read -p "Press any key to exit..."
    exit 1
fi
echo "SUCCESS: Found example_visualizations folder!"

# Run all Python files in example_visualizations
echo "[STEP 7/7] Running example visualizations..."
echo

SUCCESS_COUNT=0
TOTAL_COUNT=0

for file in example_visualizations/*.py; do
    if [ -f "$file" ]; then
        ((TOTAL_COUNT++))
        echo
        echo "================================================"
        echo "Running $file..."
        echo "================================================"
        python "$file"
        if [ $? -ne 0 ]; then
            echo
            echo "WARNING: $file failed with error code $?"
        else
            echo
            echo "SUCCESS: $file completed successfully!"
            ((SUCCESS_COUNT++))
        fi
    fi
done

echo
echo "================================================================"
echo "ALL EXAMPLES COMPLETED!"
echo "================================================================"
echo
echo "Summary:"
echo "- Successfully ran $SUCCESS_COUNT out of $TOTAL_COUNT visualization scripts"
echo "- Results saved to: example_visualizations/exports/"
echo
echo "What you'll find in the exports folder:"
echo "- .html files = Interactive charts (open in web browser)"
echo "- .png files = High-resolution images (for presentations)"
echo
echo "TIP: Navigate to example_visualizations/exports/ to see your visualizations!"
echo
read -p "Press any key to exit..." 
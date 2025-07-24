#!/bin/bash

echo "===================================================="
echo "         WAVE VISUALIZER - NO CODE LAUNCHER"
echo "===================================================="
echo
echo "This script will automatically:"
echo "  1. Install conda (if needed)"
echo "  2. Set up the environment"
echo "  3. Generate 9 political visualizations"
echo "  4. Save results as HTML + PNG files"
echo

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
        "/usr/local/Caskroom/miniconda/base/bin/conda"
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
    echo "CONDA NOT FOUND - AUTOMATIC INSTALLATION AVAILABLE"
    echo "========================================================"
    echo
    echo "We can automatically install Miniconda for you!"
    echo "This is safe and will not affect existing Python installations."
    echo
    echo "OPTION 1: Automatic Installation (Recommended)"
    echo "  - We'll download and install Miniconda3"
    echo "  - Takes 2-3 minutes"
    echo "  - Completely automatic"
    echo
    echo "OPTION 2: Manual Installation"
    echo "  - Download from: https://docs.conda.io/en/latest/miniconda.html"
    echo "  - Follow installation instructions"
    echo "  - Then run this script again"
    echo
    
    read -p "Would you like us to install conda automatically? (y/n): " INSTALL_CHOICE
    
    if [[ "${INSTALL_CHOICE,,}" =~ ^(y|yes)$ ]]; then
        # Auto-install conda
        echo
        echo "[AUTO-INSTALL] Downloading and installing Miniconda3..."
        echo "This may take a few minutes - please wait..."
        echo
        
        # Create temp directory
        TEMP_DIR="/tmp/wave_visualizer_setup"
        mkdir -p "$TEMP_DIR"
        
        # Detect OS and architecture
        OS_TYPE=$(uname -s)
        ARCH_TYPE=$(uname -m)
        
        if [[ "$OS_TYPE" == "Darwin" ]]; then
            # macOS
            if [[ "$ARCH_TYPE" == "arm64" ]]; then
                INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh"
            else
                INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
            fi
        elif [[ "$OS_TYPE" == "Linux" ]]; then
            # Linux
            if [[ "$ARCH_TYPE" == "aarch64" ]]; then
                INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
            else
                INSTALLER_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            fi
        else
            echo "ERROR: Unsupported operating system: $OS_TYPE"
            echo "Please install conda manually from: https://docs.conda.io/en/latest/miniconda.html"
            exit 1
        fi
        
        # Download installer
        echo "Downloading Miniconda3 installer for $OS_TYPE ($ARCH_TYPE)..."
        if command -v curl &> /dev/null; then
            curl -L "$INSTALLER_URL" -o "$TEMP_DIR/miniconda_installer.sh"
        elif command -v wget &> /dev/null; then
            wget "$INSTALLER_URL" -O "$TEMP_DIR/miniconda_installer.sh"
        else
            echo "ERROR: Neither curl nor wget found. Cannot download installer."
            echo "Please install conda manually from: https://docs.conda.io/en/latest/miniconda.html"
            exit 1
        fi
        
        if [ ! -f "$TEMP_DIR/miniconda_installer.sh" ]; then
            echo "ERROR: Failed to download Miniconda installer."
            echo "Please install manually from: https://docs.conda.io/en/latest/miniconda.html"
            exit 1
        fi
        
        echo "Download complete! Installing Miniconda3..."
        echo
        
        # Install Miniconda silently
        bash "$TEMP_DIR/miniconda_installer.sh" -b -p "$HOME/miniconda3"
        
        # Check if installation was successful
        if [ -f "$HOME/miniconda3/bin/conda" ]; then
            echo "SUCCESS: Miniconda3 installed successfully!"
            export PATH="$HOME/miniconda3/bin:$PATH"
            
            # Initialize conda for current shell
            source "$HOME/miniconda3/etc/profile.d/conda.sh"
            
            # Clean up installer
            rm -f "$TEMP_DIR/miniconda_installer.sh"
            rmdir "$TEMP_DIR" 2>/dev/null
            
            CONDA_FOUND=true
        else
            echo "ERROR: Installation may have failed."
            echo "Please try manual installation from: https://docs.conda.io/en/latest/miniconda.html"
            exit 1
        fi
    else
        echo "Manual installation selected."
        echo "Please download conda from: https://docs.conda.io/en/latest/miniconda.html"
        echo "After installation, run this script again."
        exit 1
    fi
fi

if [ "$CONDA_FOUND" = true ]; then
    echo "SUCCESS: Conda found and configured!"
else
    echo "ERROR: Unable to locate conda."
    exit 1
fi

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
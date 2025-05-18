#!/bin/bash

# gemini-stacktrace installer script
# This script helps users set up the gemini-stacktrace tool

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== gemini-stacktrace Installer ===${NC}"
echo "This script will help you set up gemini-stacktrace"

# Check if Python 3.11+ is installed
echo -e "\n${BLUE}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"
        PYTHON_CMD="python3"
    else
        echo -e "${RED}✗ Python 3.11+ required, but $PYTHON_VERSION detected${NC}"
        echo -e "${YELLOW}Please install Python 3.11 or newer and try again${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo -e "${YELLOW}Please install Python 3.11 or newer and try again${NC}"
    exit 1
fi

# Ask for installation method
echo -e "\n${BLUE}Choose installation method:${NC}"
echo "1) Install using pip (recommended)"
echo "2) Install using Poetry"
echo "3) Install from source"
read -p "Enter your choice (1-3): " INSTALL_METHOD

# Directory for installation
INSTALL_DIR="gemini-stacktrace"

# Install using pip
if [ "$INSTALL_METHOD" = "1" ]; then
    echo -e "\n${BLUE}Installing using pip...${NC}"
    $PYTHON_CMD -m pip install gemini-stacktrace
    INSTALL_STATUS=$?

# Install using Poetry
elif [ "$INSTALL_METHOD" = "2" ]; then
    echo -e "\n${BLUE}Installing using Poetry...${NC}"
    
    # Check if Poetry is installed
    if ! command -v poetry &>/dev/null; then
        echo -e "${YELLOW}Poetry not found. Installing Poetry...${NC}"
        curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
        
        # Add Poetry to PATH for this session
        export PATH="$HOME/.local/bin:$PATH"
        
        # Check if Poetry was installed successfully
        if ! command -v poetry &>/dev/null; then
            echo -e "${RED}✗ Failed to install Poetry${NC}"
            echo -e "${YELLOW}Please install Poetry manually and try again: https://python-poetry.org/docs/#installation${NC}"
            exit 1
        fi
    fi
    
    # Clone the repository
    git clone https://github.com/happypathway/gemini-stacktrace.git $INSTALL_DIR
    cd $INSTALL_DIR
    
    # Install dependencies
    echo -e "${BLUE}Installing dependencies with Poetry...${NC}"
    poetry install
    INSTALL_STATUS=$?
    
# Install from source
else
    echo -e "\n${BLUE}Installing from source...${NC}"
    
    # Clone the repository
    git clone https://github.com/happypathway/gemini-stacktrace.git $INSTALL_DIR
    cd $INSTALL_DIR
    
    # Create virtual environment
    echo -e "${BLUE}Creating virtual environment...${NC}"
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
    
    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -e .
    INSTALL_STATUS=$?
fi

# Check if installation was successful
if [ $INSTALL_STATUS -eq 0 ]; then
    echo -e "\n${GREEN}✓ gemini-stacktrace installed successfully!${NC}"
    
    # Setup .env file
    echo -e "\n${BLUE}Setting up environment...${NC}"
    if [ "$INSTALL_METHOD" = "1" ]; then
        echo -e "${YELLOW}Please create a .env file in your project directory with your Google API key:${NC}"
        echo -e "GOOGLE_API_KEY=\"your-gemini-api-key-here\""
    else
        echo -e "${YELLOW}Do you want to set up your Google Gemini API key now? (y/n)${NC}"
        read -p "> " SETUP_API_KEY
        
        if [ "$SETUP_API_KEY" = "y" ] || [ "$SETUP_API_KEY" = "Y" ]; then
            read -p "Enter your Google Gemini API Key: " API_KEY
            
            # Create .env file
            echo "GOOGLE_API_KEY=\"$API_KEY\"" > .env
            echo -e "${GREEN}✓ API key saved to .env file${NC}"
        else
            echo -e "${YELLOW}Please create a .env file with your Google API key before using gemini-stacktrace${NC}"
        fi
    fi
    
    # Usage instructions
    echo -e "\n${BLUE}Usage instructions:${NC}"
    if [ "$INSTALL_METHOD" = "2" ]; then
        echo -e "${GREEN}To use gemini-stacktrace with Poetry:${NC}"
        echo "cd $INSTALL_DIR"
        echo "poetry shell"
        echo "gemini-stacktrace analyze --stack-trace \"<your-stack-trace>\" --project-dir \"/path/to/your/project\""
    elif [ "$INSTALL_METHOD" = "3" ]; then
        echo -e "${GREEN}To use gemini-stacktrace:${NC}"
        echo "cd $INSTALL_DIR"
        if [ -f "venv/bin/activate" ]; then
            echo "source venv/bin/activate"
        else
            echo "source venv/Scripts/activate"
        fi
        echo "gemini-stacktrace analyze --stack-trace \"<your-stack-trace>\" --project-dir \"/path/to/your/project\""
    else
        echo -e "${GREEN}To use gemini-stacktrace:${NC}"
        echo "gemini-stacktrace analyze --stack-trace \"<your-stack-trace>\" --project-dir \"/path/to/your/project\""
    fi
    
    echo -e "\n${GREEN}Happy debugging!${NC}"
else
    echo -e "\n${RED}✗ Installation failed with error code $INSTALL_STATUS${NC}"
    echo -e "${YELLOW}Please check the error messages above and try again${NC}"
    exit 1
fi

# Installation Guide
# Windsurf Context Engineering Framework

This guide provides step-by-step instructions for installing and setting up the enhanced Windsurf Context Engineering Framework.

## 📋 Prerequisites

- **Python 3.8+** (recommended: Python 3.10 or higher)
- **pip** (Python package installer)
- **Git** (for cloning the repository)
- **Virtual environment** (recommended)

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB free space for dependencies
- **Network**: Internet connection for downloading packages

## 🚀 Quick Installation

### Option 1: Standard Installation

```bash
# Clone the repository
git clone https://github.com/windsurf/context-engineering.git
cd context-engineering

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/windsurf/context-engineering.git
cd context-engineering

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies (including development tools)
pip install -r requirements.txt -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Option 3: Using setup.py

```bash
# Clone the repository
git clone https://github.com/windsurf/context-engineering.git
cd context-engineering

# Install with all dependencies
pip install -e .[all]
```

## 📦 Dependency Categories

### Core Dependencies (Required)
These are essential for basic functionality:

- **requests**: HTTP requests for research automation
- **cryptography**: Security operations
- **pathlib**: File system operations
- **typing**: Type annotations

### Optional Dependencies
These enhance functionality but are not required:

- **pandas**: Data analysis for reports
- **rich**: Enhanced console output
- **beautifulsoup4**: Web scraping for research

### Development Dependencies
These are for development and testing:

- **pytest**: Testing framework
- **coverage**: Test coverage analysis
- **black**: Code formatting
- **pylint**: Code quality analysis
- **mypy**: Type checking

## 🔧 Configuration

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Optional: API keys for enhanced features
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional: Research automation settings
RESEARCH_CACHE_ENABLED=true
RESEARCH_CACHE_TTL=3600

# Optional: Quality guardrails settings
SECURITY_SCAN_ENABLED=true
QUALITY_CHECKS_ENABLED=true
COVERAGE_THRESHOLD=80
```

### 2. Verify Installation

Run the verification script:

```bash
python utilities/test_quality_guardrails.py
```

Expected output:
```
🛡️ Quality Guardrails Integration Test
==================================================
📁 Creating test project...
  ✅ Test project created

🔒 Testing Security Scanner...
  ✅ Security scan completed
  📊 Found X secrets
  📊 Security score: XX/100

📊 Testing Code Quality Analyzer...
  ✅ Quality analysis completed
  📊 Overall quality score: XX/100

🧪 Testing Coverage Validator...
  ✅ Coverage validation completed
  📊 Test score: XX/100

✅ ALL TESTS PASSED - Quality guardrails system is fully functional
```

## 🛠️ Component Installation

### Security Scanner Only

```bash
pip install requests cryptography bandit safety
```

### Code Quality Analyzer Only

```bash
pip install ast astroid pylint radon
```

### Test Coverage Validator Only

```bash
pip install coverage pytest pytest-cov
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'X'`

**Solution**:
```bash
# Check if virtual environment is activated
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. Permission Errors (Windows)
**Problem**: Permission denied during installation

**Solution**:
```bash
# Run as administrator or use --user flag
pip install -r requirements.txt --user
```

#### 3. SSL Certificate Errors
**Problem**: SSL certificate verification failed

**Solution**:
```bash
# Upgrade certificates
pip install --upgrade certifi

# Or use trusted hosts (temporary)
pip install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org
```

#### 4. Virtual Environment Issues
**Problem**: Virtual environment not working

**Solution**:
```bash
# Remove and recreate virtual environment
rm -rf venv  # On Windows: rmdir /s venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Platform-Specific Issues

#### Windows
- Use `python` instead of `python3`
- Use `venv\Scripts\activate` instead of `source venv/bin/activate`
- Install Visual C++ Build Tools if compilation errors occur

#### macOS
- Install Xcode Command Line Tools: `xcode-select --install`
- Use `python3` and `pip3` if multiple Python versions installed

#### Linux
- Install Python development headers: `sudo apt-get install python3-dev`
- Install system dependencies: `sudo apt-get install build-essential`

## 📊 Dependency Management

### Automatic Dependency Tracking

The framework includes automatic dependency tracking:

```bash
# Scan current dependencies
python utilities/dependency-tracker.py . 

# Update requirements files
python utilities/dependency-tracker.py . --update
```

### Manual Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages (be careful!)
pip install --upgrade -r requirements.txt
```

### Dependency Audit

```bash
# Security audit
pip install safety
safety check

# License audit
pip install pip-licenses
pip-licenses
```

## 🧪 Testing Installation

### Quick Test

```bash
python -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import requests
    import pathlib
    import typing
    print('✅ Core dependencies OK')
except ImportError as e:
    print(f'❌ Core dependency error: {e}')

# Test optional imports
try:
    import pandas
    import rich
    print('✅ Optional dependencies OK')
except ImportError:
    print('⚠️ Some optional dependencies missing (OK)')

print('🎉 Installation verification complete')
"
```

### Full Test Suite

```bash
# Run all tests
python -m pytest utilities/test_*.py -v

# Run specific component tests
python utilities/test_quality_guardrails.py
```

## 🔄 Updating

### Update Framework

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests to verify
python utilities/test_quality_guardrails.py
```

### Update Dependencies Only

```bash
# Update requirements files
python utilities/dependency-tracker.py . --update

# Install updated dependencies
pip install -r requirements.txt --upgrade
```

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**: Check `README.md` for usage instructions
2. **Run Initial Setup**: Execute `/init-context` workflow
3. **Try Examples**: Explore the `examples/` directory
4. **Configure Settings**: Customize `.env` file for your needs
5. **Join Community**: Connect with other users and contributors

## 🆘 Getting Help

If you encounter issues:

1. **Check Documentation**: Review `README.md` and workflow files
2. **Search Issues**: Look for similar problems in GitHub issues
3. **Create Issue**: Report bugs or request features
4. **Community Support**: Join our Discord/Slack community

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

**Happy coding with enhanced context engineering! 🚀**

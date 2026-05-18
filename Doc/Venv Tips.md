## Venv 


### Activate / Deactivate
```bash
# from project root
source EnvironmentSetup/activate_venv.sh

# deactivate
deactivate
```

### Install / Uninstall 
```bash
# Install multiple packages
pip install pandas numpy matplotlib paho-mqtt flask

# uninstall
pip uninstall matplotlib
```

### Export 
```bash
# After installing packages:
pip freeze > requirements.txt

# Later recreate environment with:
pip install -r EnvironmentSetup/requirements.txt
```
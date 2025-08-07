![pydoseia_logo(1)](https://github.com/user-attachments/assets/dfa5fd0f-4d20-4481-8ca8-a90dc9dbe627) 
# pyDOSEIA
**A python-based package for computation of Dose from atmospheric release**

---

## 📖 Description
 We introduce **pyDOSEIA**, a robust Python package, designed for radiation risk assessment and dose calculation in scenarios such as nuclear events, radiological accidents, and environmental contamination. Built on advanced computational models, it offers tools for estimating doses from various exposure pathways like inhalation, ingestion, external exposure, and plume shine. Featuring parallel processing and up-to-date dose conversion factors, pyDOSEIA ensures accurate calculations for both short-term and long-term exposures. With a user-friendly input generator module, it empowers researchers and policymakers in radiation risk assessment and emergency preparedness.

> [!IMPORTANT]
>**🚀 BIG NEWS!!!** pyDOSEIA article is now accepted for publication at Health Physics journal!! Link will be shared shortly.

## A Simple pyDOSEIA flowchart
![fig1(1)](https://github.com/user-attachments/assets/45cfc567-2ac9-48e4-9511-4f799767b049)

---

## INGEN (Interactive Input Generator) flowchart
![pydoseia_test_cases](https://github.com/user-attachments/assets/6be3e18f-e297-43e0-9e0c-7cff780a9da9)

---

## Installation

### ONLINE INSTALLATION
> [!NOTE]
> If your organization has firewalls and restrictions then configure the *`.condarc`* and *`pip.ini`* file to the channels of your organizations
- [ ] Link video/Guide to demonstrate configuration
- [ ] Corectly place requirements.txt file 

The installation guides for these environments are provided below:
```bash
conda create -n pydose python=3.10
conda activate pydose
conda install --file requirements.txt

#if above one didn't work
pip install -r requirements.txt
```

### OFFLINE INSTALLATION

1. Download the pyDOSEIA package from GitHub & unzip it.
2. Download the latest version of Anaconda from [Anaconda Downloads](https://www.anaconda.com/download) (Windows and Linux; macOS is not tested).
>> Install Anaconda using the instructions provided in the [Anaconda Installation Guide](https://docs.anaconda.com/anaconda/install/).
3. Verify Anaconda installation:
   ```bash
   conda list
   ```
4. Place the pyDOSEIA package (after unzipping) on the same disk (C:, D:, or E: as applicable for Windows) to make it easy to track the code.

#### ❌ Without requirements.txt
- Manually download & install required packages:
   - [Joblib](https://github.com/joblib/joblib) (for parallel computing)
   - [xlrd 2.0.1](https://pypi.org/project/xlrd/#files) for reading Excel
- On machine with internet create a dedicated folder to store required packages eg. 'offline_packages' and type:
```bash
pip download joblib -d "C:\path\to\your\offline_packages"
pip download xlrd -d "C:\path\to\your\offline_packages"
```
- Copy paste the folder into offline machine and install packages using:
```bash
pip install --no-index --find-links "D:\path\to\your\offline_packages" -r requirements.txt
```

#### ✅ With requirements.txt (Recommended)
- In Anaconda Command Prompt:
   - On machine with internet create a dedicated folder to store required packages eg. 'offline_packages' and type:
   ```bash
   pip download -r requirements.txt -d "C:\path\to\your\all-offline-packages"
   ```
   - Copy paste the folder into offline machine and install packages using:
   ```bash
    pip install --no-index --find-links "\path\to\your\offline-joblib-packages" joblib
   ```
    - Install and setup xlrd

5. Confirm installations by running `conda list` 
6. pyDOSEIA is now ready for use. Follow the instructions in the USAGE section of README file for running pyDOSEIA.

---

## Usage

### 🧾 CLI Mode
run Interactive Input Generator using following command:
python auto_input_generator.py

It will prompt questions with hints on how to answer it. Follow it to generate the input file (example of input file given in config directory). Once all asked questions are answered by the user, the code automatically initiate computation.

If input is already created, user are requested to run auto_input_generator.py and provide the directory name and name of the existing input file name. pyDOSEIA automatically detect the input file and run computation using existing input.

optional option in input file: pickle_it == False (default)
With pickle_it:True, pickle files are written using output of dilution factor and dose computations. This is highly useful for analizing the data for research, analysis and machine/deep learning application. 

NOTE: If one of the radionuclide in the input is H-3, it should be the last entry of the list of radionuclides.

The progam now outputs multiple csv files for summary statistics along with standard detailed output document.

## 🌐 NEW: Streamlit GUI (v1.0)

---

**Contributing** 

We welcome contributions to the pyDOSEIA project! If you have suggestions, want to improve the code, or have ideas for new features, please create a Pull Request or raise an issue. If you encounter any bugs or have questions about using the package, don't hesitate to contact us. Your feedback and contributions are invaluable in making pyDOSEIA a better tool for the community.

**Contact information**

Copyright(C) 2023 Authors and Developers: Dr. Biswajit Sadhu (biswajit.chem001@gmail.com), Dr. Tanmay Sarkar (tanmays@barc.gov.in).

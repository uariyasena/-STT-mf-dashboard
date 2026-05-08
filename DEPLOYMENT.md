# MF Dashboard Deployment Guide

## Option 1: Windows Server Deployment

### Prerequisites
- Windows Server with Python 3.14+ installed
- Access to company network
- JIRA API token

### Steps

1. **Copy files to server**
   ```bash
   # Copy the entire dashboard folder to:
   C:\inetpub\mf-dashboard\
   ```

2. **Install dependencies**
   ```bash
   cd C:\inetpub\mf-dashboard
   python -m pip install -r requirements.txt
   ```

3. **Configure JIRA credentials**
   - Edit `.env` file
   - Add your JIRA_AUTH_TOKEN and JIRA_USER_EMAIL

4. **Create startup script** (`start_dashboard.bat`):
   ```batch
   @echo off
   cd C:\inetpub\mf-dashboard
   C:\Python314\python.exe -m streamlit run mf_dashboard_creative.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
   ```

5. **Set up Windows Service** (using NSSM - Non-Sucking Service Manager):
   ```bash
   # Download NSSM from https://nssm.cc/download
   nssm install MFDashboard "C:\inetpub\mf-dashboard\start_dashboard.bat"
   nssm start MFDashboard
   ```

6. **Access the dashboard**:
   - From company network: `http://server-name:8501`
   - Or use server IP: `http://192.168.x.x:8501`

---

## Option 2: Docker Deployment

### Prerequisites
- Docker Desktop or Docker on server
- docker-compose

### Steps

1. **Build and run**
   ```bash
   cd dashboard
   docker-compose up -d
   ```

2. **Access the dashboard**:
   - `http://localhost:8501`
   - `http://server-ip:8501`

3. **Stop the dashboard**:
   ```bash
   docker-compose down
   ```

---

## Removing the Password Requirement

The dashboard currently requires JIRA authentication to fetch live status. Options:

### Option A: Pre-configure credentials on server
- Set `JIRA_AUTH_TOKEN` in server environment variables
- Users won't see or need to enter credentials
- **Current setup** - credentials are in `.env` file on server

### Option B: Read-only mode (no JIRA)
- Users can view the dashboard without JIRA credentials
- Status will show as "Unknown" for all tickets
- Edit `jira_data_fetcher.py` to handle missing credentials gracefully

### Option C: SSO/Active Directory integration
- Integrate with company's authentication system
- Requires custom development

---

## Security Considerations

⚠️ **IMPORTANT:**
- Never commit `.env` file with real credentials to Git
- Restrict server access to authorized users only
- Use HTTPS if exposing outside company network
- Keep JIRA token secure (read-only permissions recommended)

---

## Troubleshooting

**Dashboard not accessible:**
- Check Windows Firewall: Allow port 8501
- Verify service is running: `nssm status MFDashboard`

**JIRA data not updating:**
- Check `.env` credentials are correct
- Verify JIRA API token hasn't expired
- Check server has internet access to reach Jira

**Excel file not updating:**
- Make sure the Excel file path in `config.yaml` is correct
- Ensure server has read permissions to the Excel file location

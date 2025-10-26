# DMRB Dashboard - Configuration Guide

## 📋 Data Source Configuration

The DMRB Dashboard supports loading data from two sources:
- **Local Excel file** (default)
- **Google Sheets** (for cloud deployment)

## 🔧 Setup Instructions

### Option 1: Local File (Default)

1. Place your Excel file at: `data/DRMB.xlsx`
2. No configuration needed - this is the default mode
3. Run the app: `streamlit run app.py`

### Option 2: Google Sheets

#### Step 1: Publish Your Google Sheet

1. Open your Google Sheet
2. Go to **File → Share → Publish to web**
3. Select **Entire Document**
4. Choose format: **Microsoft Excel (.xlsx)**
5. Click **Publish**
6. Copy the generated URL (should end with `/export?format=xlsx`)

Example URL:
```
https://docs.google.com/spreadsheets/d/1alxeq1eGB6nbDXWhKh5O34FQkFcXkYOI/export?format=xlsx
```

#### Step 2: Configure Streamlit Secrets

Create `.streamlit/secrets.toml` file:

```toml
[data]
DATA_SOURCE = "gdrive"
GDRIVE_XLSX_URL = "YOUR_GOOGLE_SHEETS_EXPORT_URL_HERE"
```

#### Step 3: Deploy to Streamlit Cloud

1. Push your code to GitHub (excluding `secrets.toml`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. In **Advanced settings → Secrets**, paste:

```toml
[data]
DATA_SOURCE = "gdrive"
GDRIVE_XLSX_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=xlsx"
```

5. Deploy!

## 🔄 Auto-Refresh

The dashboard automatically refreshes data every **5 minutes** when running.

You can also manually refresh:
- Click **🔄 Refresh Data** button in the sidebar
- All cached data will be cleared and reloaded

## 📊 Required Sheets

Your Excel file must contain these sheets:
- `Unit` - Unit information
- `Task` - Task tracking data

## 🛠️ Environment Variables (Alternative to Secrets)

You can also use environment variables instead of secrets:

```bash
export DATA_SOURCE="gdrive"
export GDRIVE_XLSX_URL="https://docs.google.com/spreadsheets/d/..."
streamlit run app.py
```

## 🔐 Security Notes

- **Never commit** `.streamlit/secrets.toml` to version control
- Add it to `.gitignore`
- Use Streamlit Cloud's secrets manager for deployment
- The `.streamlit/secrets.toml.template` file is safe to commit

## 📝 Troubleshooting

### "File not found" error
- Check that `data/DRMB.xlsx` exists (local mode)
- Verify the Google Sheets URL is correct (gdrive mode)

### "Failed to download" error
- Ensure your Google Sheet is published to web
- Check that the URL ends with `/export?format=xlsx`
- Verify your internet connection

### Data not updating
- Click the **🔄 Refresh Data** button manually
- Check the "Last Updated" timestamp in the sidebar
- Verify auto-refresh is enabled (shows "🔁 Auto-refresh: 5 min")

## 🎯 Best Practices

1. **Local Development**: Use `DATA_SOURCE="local"` for faster iterations
2. **Production/Cloud**: Use `DATA_SOURCE="gdrive"` for easy updates
3. **Data Updates**: Edit the Google Sheet directly - changes appear within 5 minutes
4. **Manual Refresh**: Use when you need immediate updates

## 📚 File Structure

```
DMRB/
├── .streamlit/
│   ├── config.toml           # Streamlit app config
│   ├── secrets.toml          # Your secrets (gitignored)
│   └── secrets.toml.template # Template for reference
├── data/
│   └── DRMB.xlsx            # Local Excel file (if using local mode)
├── src/
│   └── core/
│       ├── datasource.py    # Data source handler
│       └── data_loader.py   # Sheet loaders
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

**Local mode:**
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Google Sheets mode:**
```bash
# Copy template
cp .streamlit/secrets.toml.template .streamlit/secrets.toml

# Edit secrets.toml with your Google Sheets URL
# Set DATA_SOURCE = "gdrive"

pip install -r requirements.txt
streamlit run app.py
```

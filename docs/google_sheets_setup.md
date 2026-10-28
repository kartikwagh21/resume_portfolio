# Google Sheets 2-Way Sync Setup Guide

This guide explains how to connect **CareerVault & ResumeForge AI** to your Google account for two-way portfolio synchronization.

---

## 1. Google Cloud Console Configuration

1. Visit the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one (e.g., `careervault-portfolio-sync`).
3. In the left navigation bar, go to **APIs & Services > Library**.
4. Search for and enable the following two APIs:
   - **Google Sheets API**
   - **Google Drive API**

---

## 2. Create a Service Account

1. In the Google Cloud Console, navigate to **IAM & Admin > Service Accounts**.
2. Click **Create Service Account**:
   - **Service Account Name**: `careervault-sheets-sync`
   - **Service Account ID**: `careervault-sheets-sync`
3. Click **Create and Continue**.
4. (Optional) For Role, select **Editor** or leave default. Click **Done**.
5. Find your newly created service account in the table and click on it.
6. Navigate to the **Keys** tab -> click **Add Key > Create New Key**.
7. Select **JSON** and click **Create**.
8. A JSON file will automatically download to your computer.

---

## 3. Place Service Account Key in the Backend

1. Rename the downloaded file to `service_account.json`.
2. Move it to the `backend/` directory:
   ```bash
   cp ~/Downloads/your-downloaded-key.json /Users/kartikwagh/portfolio/backend/service_account.json
   ```
3. Ensure `service_account.json` is listed in your `.gitignore` (CareerVault includes this in `.gitignore` by default to prevent accidental commits).

---

## 4. Create and Share Your Google Sheet

1. Open [Google Sheets](https://sheets.new) and create a new blank spreadsheet (e.g., "My Professional Portfolio").
2. Copy the Spreadsheet ID from the URL bar:
   `https://docs.google.com/spreadsheets/d/`**`<SPREADSHEET_ID>`**`/edit`
3. Click the **Share** button in the top right of Google Sheets.
4. Paste the Service Account email address:
   (You can find this in `service_account.json` under `"client_email"` or displayed in the CareerVault Sync modal in the UI).
5. Grant the Service Account **Editor** permissions and click **Share**.

---

## 5. Configure `.env`

Add the Spreadsheet ID to `backend/.env`:
```env
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

---

## 6. Offline / Mock Mode

If you do not have a Google Service Account right now, CareerVault includes an intelligent **Mock Sandbox Sync Mode**:
- You can still click **Export to Sheet** and **Sync from Sheet** in the UI.
- All 10 category tables are serialized, tracked with timestamps, and can be synchronized back into the database.
- A status badge in the header shows whether live Google Sheets or Mock Mode is currently active.

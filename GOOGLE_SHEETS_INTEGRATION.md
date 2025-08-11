# Google Sheets Integration for KEF Assessment Dashboard

## Overview

The KEF Assessment Dashboard now includes comprehensive Google Sheets integration that allows automatic importing of assessment responses from Google Sheets. This integration polls Google Sheets at configurable intervals and processes new data automatically.

## Features

- **Automatic Data Import**: Polls Google Sheets every N minutes for new data
- **Kannada Text Processing**: Converts Kannada assessment responses to numeric values
- **Error Handling**: Failed imports are tracked and can be retried
- **Manual Controls**: Manual import triggers and configuration management
- **Real-time Monitoring**: Live statistics and status monitoring

## Setup Instructions

### 1. Prepare Your Google Sheet

1. Create a Google Sheet with assessment data
2. Ensure the sheet has the following columns (in order):
   - Date (YYYY-MM-DD format)
   - Student Name
   - Assessment Response (Kannada or English)
   - Index ID (question identifier)
3. Make the sheet publicly accessible:
   - Go to Share > Change to anyone with the link can view
   - Or ensure appropriate sharing permissions

### 2. Configure in Dashboard

1. Navigate to **Maintenance** page in the dashboard
2. Click on the **Google Sheets** tab
3. Enter your Google Sheets URL in the configuration form
4. Set the polling interval (1-1440 minutes)
5. Enable the integration by checking "Active"
6. Click **Save Configuration**

### 3. Test Connection

1. Click **Test Connection** to verify the sheet is accessible
2. Check that the connection status shows "Active"
3. Verify the row count matches your expectations

## Text Conversion Mappings

The system automatically converts Kannada assessment responses to numeric values:

| Kannada Text | English Equivalent | Numeric Value |
|--------------|-------------------|---------------|
| ಸಾಧಿಸಿದ್ದಾರೆ | achieved/accomplished | 1 |
| ಪ್ರಗತಿಯಲ್ಲಿದ್ದಾರೆ | in progress/progressing | 0.5 |
| ಕಲಿಯುತ್ತಿದ್ದಾರೆ | learning/developing | 0 |

## Background Polling Service

### Running the Standalone Poller

For production environments, run the standalone polling service:

```bash
# Run continuously (recommended for production)
python sheets_poller.py

# Run once and exit (useful for testing)
python sheets_poller.py --once
```

### Service Configuration

The poller reads configuration from the database and:
- Fetches new rows since the last processed row
- Converts text responses to numeric values
- Inserts valid responses into the responses table
- Records failed imports for manual review
- Logs all activities to `sheets_poller.log`

## Managing Failed Imports

### Viewing Failed Imports

1. Go to Maintenance > Google Sheets tab
2. Click **View Failed Imports** to see detailed error information
3. Review the error messages and raw data

### Retrying Failed Imports

- **Single Retry**: Click the retry button next to individual failed imports
- **Retry All**: Use "Retry All" button to re-attempt all failed imports
- **Manual Fix**: Edit the source data in Google Sheets and retry

### Deleting Failed Imports

- Remove failed import records that cannot be fixed
- Use "Delete All" to clear all failed import records

## Monitoring and Statistics

The dashboard provides real-time monitoring:

- **Last Import**: Timestamp of most recent import
- **Last Row Processed**: Current position in the sheet
- **Total Imported**: Number of successfully imported responses
- **Failed Imports**: Count of import failures
- **Next Poll**: Estimated time for next automatic import

## API Endpoints

The integration provides REST API endpoints for external automation:

- `GET /api/sheets/config` - Get current configuration
- `POST /api/sheets/config` - Update configuration
- `POST /api/sheets/test` - Test sheet connection
- `GET /api/sheets/stats` - Get import statistics
- `POST /api/sheets/import` - Trigger manual import
- `POST /api/sheets/deactivate` - Deactivate polling

## Troubleshooting

### Common Issues

1. **"Sheet not accessible"**
   - Verify sharing permissions
   - Check URL format
   - Ensure sheet exists

2. **"No new data found"**
   - Verify there are rows beyond last_row_processed
   - Check data format in source sheet

3. **"Text conversion failed"**
   - Ensure assessment responses use supported Kannada/English terms
   - Check for typos in response text

4. **Background service not running**
   - Check `sheets_poller.log` for errors
   - Verify database connectivity
   - Restart the polling service

### Log Files

- **Application Logs**: Check Flask application logs for API errors
- **Poller Logs**: Check `sheets_poller.log` for background service issues
- **Database Logs**: Check database connection and query issues

## Security Considerations

- Use read-only Google Sheets sharing when possible
- Regularly review access logs
- Monitor for unusual polling patterns
- Keep polling intervals reasonable to avoid rate limiting

## Performance Tips

- Set appropriate polling intervals (5-15 minutes typical)
- Monitor database size and performance
- Consider archiving old responses if needed
- Use manual imports for large initial data loads

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files for error details
3. Verify Google Sheets accessibility and format
4. Test with manual import before automated polling

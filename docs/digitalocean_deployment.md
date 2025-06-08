# DigitalOcean App Platform Deployment Guide

This guide provides step-by-step instructions for deploying the Enhanced Voice Cloning Application to DigitalOcean App Platform.

## Prerequisites

- A DigitalOcean account
- GitHub repository with the application code
- Basic familiarity with DigitalOcean App Platform

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository has the following files:
- `requirements.txt` with all dependencies
- `app.py` as the main application file
- All necessary application code and assets

### 2. Create a New App on DigitalOcean App Platform

1. Log in to your DigitalOcean account
2. Navigate to the App Platform section
3. Click "Create App"
4. Select your GitHub repository
5. Choose the branch you want to deploy (usually `main`)

### 3. Configure the App

1. **Resource Type**: Select "Web Service"
2. **Source Directory**: Set to `/` (root directory)
3. **Build Command**: `pip install -r requirements.txt`
4. **Run Command**: `python run.py --host 0.0.0.0 --port 8080`
5. **Environment Variables**: Add any necessary environment variables

### 4. Configure Resources

1. Select an appropriate plan based on your needs
2. For optimal performance with voice processing, choose a plan with at least:
   - 2 GB RAM
   - 1 vCPU
   - For GPU acceleration, select a plan with GPU support if available

### 5. Review and Launch

1. Review all settings
2. Click "Launch App"
3. Wait for the build and deployment process to complete

### 6. Access Your Application

Once deployed, you can access your application at the URL provided by DigitalOcean:
`https://your-app-name.ondigitalocean.app`

## Updating Your Application

To update your application after making changes:

1. Push changes to your GitHub repository
2. DigitalOcean will automatically detect changes and redeploy
3. Monitor the deployment progress in the DigitalOcean dashboard

## Troubleshooting

If you encounter issues during deployment:

1. Check the build logs in the DigitalOcean dashboard
2. Ensure all dependencies are correctly listed in `requirements.txt`
3. Verify that the run command is correct
4. Check that your application is configured to listen on the correct port (8080)

## Scaling

To handle increased traffic or processing needs:

1. Navigate to your app in the DigitalOcean dashboard
2. Go to the "Settings" tab
3. Under "Resources", adjust the number of containers or select a larger plan

## Monitoring

Monitor your application's performance:

1. Use the "Metrics" tab in the DigitalOcean dashboard
2. Set up alerts for CPU, memory, or disk usage
3. Review logs regularly to identify any issues

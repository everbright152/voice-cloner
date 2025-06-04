# DigitalOcean Deployment Guide

This guide provides step-by-step instructions for deploying the Voice Cloning Web Application to DigitalOcean.

## Option 1: DigitalOcean App Platform (Recommended)

### Prerequisites
- DigitalOcean account
- GitHub account (for repository hosting)
- Chatterbox API key

### Step 1: Prepare Your Repository
1. Push your code to a GitHub repository
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/voice-cloning-app.git
   git push -u origin main
   ```

### Step 2: Create a New App on DigitalOcean App Platform
1. Log in to your DigitalOcean account
2. Navigate to the App Platform section
3. Click "Create App"
4. Select GitHub as the source
5. Connect your GitHub account if not already connected
6. Select the voice-cloning-app repository
7. Select the branch to deploy (usually `main`)

### Step 3: Configure Your App
1. Select "Web Service" as the component type
2. Choose "Dockerfile" as the build method
3. Set the HTTP port to 8000
4. Configure environment variables:
   - `CHATTERBOX_API_KEY`: Your Resemble AI Chatterbox API key
   - `DATABASE_URL`: `sqlite:///./app.db` (or your preferred database URL)

### Step 4: Configure Resources
1. Choose an appropriate plan (Basic: $5/month is sufficient for starting)
2. Select the region closest to your target users

### Step 5: Finalize and Deploy
1. Review your app configuration
2. Click "Launch App"
3. Wait for the build and deployment process to complete

### Step 6: Access Your Application
1. Once deployed, you'll receive a URL to access your application
2. You can configure a custom domain in the App settings if desired

## Option 2: DigitalOcean Droplet

### Prerequisites
- DigitalOcean account
- SSH key pair
- Chatterbox API key

### Step 1: Create a Droplet
1. Log in to your DigitalOcean account
2. Click "Create" and select "Droplets"
3. Choose an image: Ubuntu 22.04 LTS
4. Select a plan: Basic ($5/month is sufficient for starting)
5. Choose a datacenter region closest to your target users
6. Add your SSH key
7. Click "Create Droplet"

### Step 2: Connect to Your Droplet
```bash
ssh root@your_droplet_ip
```

### Step 3: Install Docker and Docker Compose
```bash
# Update package lists
apt update

# Install required packages
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

# Add Docker repository
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package lists again
apt update

# Install Docker
apt install -y docker-ce

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Step 4: Clone Your Repository
```bash
# Install Git
apt install -y git

# Clone your repository
git clone https://github.com/yourusername/voice-cloning-app.git
cd voice-cloning-app
```

### Step 5: Configure Environment Variables
```bash
# Create .env file
cat > .env << EOL
CHATTERBOX_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./app.db
EOL
```

### Step 6: Build and Run the Application
```bash
# Build and start the containers
docker-compose up -d --build
```

### Step 7: Set Up Nginx for SSL (Optional but Recommended)
```bash
# Install Nginx and Certbot
apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx
cat > /etc/nginx/sites-available/voice-cloning-app << EOL
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# Enable the site
ln -s /etc/nginx/sites-available/voice-cloning-app /etc/nginx/sites-enabled/

# Test Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx

# Set up SSL certificate
certbot --nginx -d your-domain.com
```

### Step 8: Access Your Application
Your application should now be accessible at your domain or droplet IP address.

## Maintenance and Updates

### Updating Your Application
```bash
# Pull latest changes
git pull

# Rebuild and restart containers
docker-compose down
docker-compose up -d --build
```

### Monitoring Logs
```bash
# View application logs
docker-compose logs -f
```

### Backup Database
```bash
# Create a backup directory
mkdir -p backups

# Backup the SQLite database
cp app.db backups/app_$(date +%Y%m%d%H%M%S).db
```

## Troubleshooting

### Container Not Starting
Check the logs for errors:
```bash
docker-compose logs
```

### Application Not Accessible
Check if the container is running:
```bash
docker ps
```

Check if the port is open:
```bash
netstat -tulpn | grep 8000
```

### Database Issues
Check database permissions:
```bash
ls -la app.db
chmod 666 app.db  # If needed
```

## Security Considerations

1. **API Key Protection**: Ensure your Chatterbox API key is stored securely
2. **Firewall Configuration**: Configure UFW to restrict access
   ```bash
   ufw allow ssh
   ufw allow http
   ufw allow https
   ufw enable
   ```
3. **Regular Updates**: Keep your system and dependencies updated
   ```bash
   apt update && apt upgrade -y
   ```
4. **User Management**: Create a non-root user for daily operations
   ```bash
   adduser appuser
   usermod -aG docker appuser
   ```

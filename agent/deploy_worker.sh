#!/bin/bash

echo "Cloudflare Worker Deployment Script"
echo "==================================="
echo

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Installing Wrangler CLI..."
    npm install -g wrangler
fi

# Create wrangler.toml
cat > wrangler.toml << 'EOF'
name = "vandine-agent"
main = "cloudflare-worker.js"
compatibility_date = "2024-01-01"

[env.production]
workers_dev = true
route = "agent.vandine.us/*"

[env.production.vars]
AUTH_TOKEN = "secret_auth_token_123"
PI_EXECUTOR_URL = "http://192.168.2.7:8000"
EOF

echo "Created wrangler.toml configuration"
echo

# Check authentication
echo "Checking Cloudflare authentication..."
echo "If not logged in, run: wrangler login"
echo

# Deploy options
echo "Deployment options:"
echo "1. Deploy to workers.dev subdomain (free)"
echo "2. Deploy to custom domain (requires zone setup)"
echo "3. Test locally first"
echo

read -p "Choose option (1-3): " option

case $option in
    1)
        echo "Deploying to workers.dev..."
        wrangler deploy --env production
        echo
        echo "✅ Worker deployed!"
        echo "Access at: https://vandine-agent.[your-subdomain].workers.dev"
        ;;
    2)
        echo "Setting up custom domain..."
        echo "First, add a CNAME record in Cloudflare:"
        echo "  Name: agent"
        echo "  Target: [your-subdomain].workers.dev"
        echo
        read -p "Press Enter when DNS is configured..."
        wrangler deploy --env production
        echo
        echo "✅ Worker deployed to custom domain!"
        ;;
    3)
        echo "Starting local development server..."
        wrangler dev --port 8787
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

#!/usr/bin/env python3
"""
Helper script to get Cloudflare account information
"""
import os
import sys
import json

def main():
    print("Cloudflare Credential Helper")
    print("="*50)
    print()
    print("To get your Cloudflare credentials:")
    print()
    print("1. API Token (Recommended):")
    print("   - Go to: https://dash.cloudflare.com/profile/api-tokens")
    print("   - Click 'Create Token'")
    print("   - Use 'Edit zone DNS' template or create custom")
    print("   - Required permissions:")
    print("     * Zone:DNS:Read/Edit")
    print("     * Zone:Cache Purge:Purge")
    print("     * Zone:Page Rules:Read/Edit")
    print("     * Account:Cloudflare Workers:Read/Edit")
    print()
    print("2. Account ID:")
    print("   - Go to any domain in Cloudflare dashboard")
    print("   - Right sidebar shows 'Account ID'")
    print()
    print("3. Zone ID:")
    print("   - Go to your domain (vandine.us) in dashboard")
    print("   - Right sidebar shows 'Zone ID'")
    print()
    print("-"*50)
    print("Quick check for vandine.us:")
    print("Zone likely matches: vandine.us")
    print()
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to view current settings? (y/n): ")
        if response.lower() == 'y':
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key = line.split('=')[0]
                        print(f"  {key} is configured")
    else:
        print("📝 Ready to create .env file")
        response = input("Do you want to create it now? (y/n): ")
        if response.lower() == 'y':
            print("\nEnter your credentials (or press Enter to skip):")
            
            api_token = input("API Token: ").strip()
            account_id = input("Account ID: ").strip()
            zone_id = input("Zone ID: ").strip()
            
            with open('.env', 'w') as f:
                f.write(f"# Cloudflare API Configuration\n")
                f.write(f"CLOUDFLARE_API_TOKEN={api_token or 'your_api_token_here'}\n")
                f.write(f"CLOUDFLARE_ACCOUNT_ID={account_id or 'your_account_id_here'}\n")
                f.write(f"CLOUDFLARE_ZONE_ID={zone_id or 'your_zone_id_here'}\n")
                f.write(f"\n# Worker Configuration\n")
                f.write(f"WORKER_URL=https://agent.vandine.workers.dev\n")
                f.write(f"WORKER_AUTH_TOKEN=secret_auth_token_123\n")
                f.write(f"\n# Pi Executor Configuration\n")
                f.write(f"PI_EXECUTOR_PORT=8000\n")
                f.write(f"PI_EXECUTOR_HOST=0.0.0.0\n")
            
            print("\n✅ .env file created!")
            print("You can edit it later with: nano .env")

if __name__ == '__main__':
    main()

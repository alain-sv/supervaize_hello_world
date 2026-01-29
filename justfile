# Justfile 
default:
    @just --list

# Send the environment variables to Vercel 
vercel_add_env:
    vercel env add SUPERVAIZE_API_URL 
    vercel env add SUPERVAIZE_API_KEY --sensitive
    vercel env add SUPERVAIZE_WORKSPACE_ID 
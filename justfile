# Justfile 
default:
    @just --list

# Send the environment variables to Vercel 
vercel_add_env:
    echo $SUPERVAIZE_API_URL | vercel env add SUPERVAIZE_API_URL production
    echo $SUPERVAIZE_API_KEY | vercel env add SUPERVAIZE_API_KEY production --sensitive
    echo $SUPERVAIZE_WORKSPACE_ID | vercel env add SUPERVAIZE_WORKSPACE_ID production
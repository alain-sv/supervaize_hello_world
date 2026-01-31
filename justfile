# Justfile 
default:
    @just --list

# Send the environment variables to Vercel 
vercel_add_env:
    echo $SUPERVAIZE_API_URL | vercel env add SUPERVAIZE_API_URL production --force
    echo $SUPERVAIZE_API_KEY | vercel env add SUPERVAIZE_API_KEY production --sensitive --force
    echo $SUPERVAIZE_WORKSPACE_ID | vercel env add SUPERVAIZE_WORKSPACE_ID production --force
    echo $SUPERVAIZER_HOST | vercel env add SUPERVAIZER_HOST production --force
    echo $SUPERVAIZER_PORT | vercel env add SUPERVAIZER_PORT production --force
    echo $SUPERVAIZER_SCHEME | vercel env add SUPERVAIZER_SCHEME production --force
    echo $SUPERVAIZE_PUBLIC_URL | vercel env add SUPERVAIZE_PUBLIC_URL production --force

vercel_redeploy:
    vercel --prod

# Test locally with Vercel
vercel_dev:
    vercel dev
# Web Deployment Guide

This guide explains how to deploy the Medusa Wavetable Utility web interface to various hosting platforms.

## Quick Local Testing

```bash
# Install dependencies
pip install -r requirements_web.txt

# Run development server
./run_web.sh
# Or manually:
python web_app.py
```

The app will be available at `http://localhost:5001`

**Note:** Port 5001 is used by default to avoid conflicts with macOS AirPlay Receiver (which uses port 5000).

## Production Deployment Options

### 1. Vercel (Recommended - Free)

Create `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "web_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "web_app.py"
    }
  ]
}
```

Deploy:
```bash
npm i -g vercel
vercel --prod
```

### 2. Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### 3. Render

1. Connect your GitHub repo to Render
2. Set build command: `pip install -r requirements_web.txt`
3. Set start command: `python web_app.py`

### 4. PythonAnywhere

1. Upload files to PythonAnywhere
2. Create a new web app
3. Set WSGI file to point to your app
4. Install dependencies in console

### 5. DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: medusa-tools
services:
- name: web
  source_dir: /
  github:
    repo: your-username/medusa_tools
    branch: main
  run_command: python web_app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
```

## Environment Variables

For production, set:
- `FLASK_ENV=production`
- `SECRET_KEY=your-secret-key`

## File Upload Limits

Default: 100MB max upload
To change, modify `MAX_CONTENT_LENGTH` in `web_app.py`

## Security Considerations

- Files are automatically deleted after 1 hour
- Use HTTPS in production
- Set a strong secret key
- Consider rate limiting for public deployments

## Cost Estimates

- **Vercel Free**: Good for personal use
- **Railway**: ~$5/month for basic usage
- **Render**: Free tier available
- **DigitalOcean**: ~$5/month for basic droplet

## Monitoring

Add basic monitoring:
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
``` 
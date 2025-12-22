# Cloudinary Setup for Profile Images on Render.com

## Problem
Render.com's free tier doesn't have persistent storage. Uploaded files (like profile images) are deleted when the app redeploys.

## Solution
Use **Cloudinary** (free tier) for storing media files persistently.

---

## Step 1: Create Free Cloudinary Account

1. Go to https://cloudinary.com/users/register_free
2. Sign up for a **free account**
3. After signup, go to your Dashboard: https://console.cloudinary.com/

---

## Step 2: Get Your Cloudinary Credentials

On your Cloudinary Dashboard, you'll see:
- **Cloud Name**: (e.g., `dxxxxx`)
- **API Key**: (e.g., `123456789012345`)
- **API Secret**: (e.g., `abcdefghijklmnopqrs`)

**Keep these safe!** You'll need them in the next step.

---

## Step 3: Add Environment Variables to Render.com

1. Go to your Render.com dashboard: https://dashboard.render.com/
2. Click on your **connectflow-pro** web service
3. Go to **Environment** tab
4. Click **Add Environment Variable** and add these three variables:

   ```
   CLOUDINARY_CLOUD_NAME = your-cloud-name
   CLOUDINARY_API_KEY = your-api-key
   CLOUDINARY_API_SECRET = your-api-secret
   ```

5. Click **Save Changes**

---

## Step 4: Deploy

Render will automatically redeploy when you push the changes to GitHub (already done).

Once deployed:
1. Upload a new profile image
2. The image will be stored on Cloudinary
3. Images will persist even after redeployments!

---

## How It Works

- All uploaded images go to Cloudinary's cloud storage
- Django generates URLs pointing to Cloudinary's CDN
- Images load fast from Cloudinary's global CDN
- Free tier includes: 25 GB storage + 25 GB bandwidth/month

---

## Testing Locally (Optional)

If you want to test locally with Cloudinary:

1. Create a `.env` file in your project root:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

2. Install python-decouple if not already:
   ```
   pip install python-decouple
   ```

3. Update your local settings to use Cloudinary (optional)

---

## Free Tier Limits

- **Storage**: 25 GB
- **Bandwidth**: 25 GB/month
- **Transformations**: 25 credits/month
- **Users**: Unlimited

This is more than enough for a team collaboration app!

---

## Alternative: WhiteNoise for Static Files

Note: This setup only affects **media files** (user uploads like avatars).
**Static files** (CSS, JS, images in your codebase) are still served by WhiteNoise, which is perfect for Render.

---

## Troubleshooting

**Images still not showing?**
1. Check Environment Variables are set correctly in Render
2. Check Render deployment logs for errors
3. Verify Cloudinary credentials are correct
4. Hard refresh your browser (Ctrl+Shift+R)

**"Cloudinary not configured" error?**
- Make sure all 3 environment variables are set in Render
- Redeploy after adding environment variables

---

## Next Steps After Setup

Once configured, your profile images will work permanently! 🎉

The app will automatically:
- Upload new avatars to Cloudinary
- Generate secure CDN URLs
- Display images from Cloudinary's fast global network

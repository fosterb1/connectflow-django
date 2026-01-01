# Firebase Email Verification Troubleshooting Guide

## Issue: Users Not Receiving Verification Emails

### Problem
Users signing up are not receiving email verification messages from Firebase Authentication.

---

## ✅ Solution Checklist

### 1. Enable Email/Password Authentication in Firebase Console

**Steps:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **connectflowpro-f1202**
3. Click **Authentication** (left sidebar)
4. Go to **Sign-in method** tab
5. Find **Email/Password** provider
6. Make sure it's **ENABLED** (toggle should be blue/on)
7. Click **Save** if you made changes

---

### 2. Configure Email Templates

**Steps:**
1. In Firebase Console → **Authentication**
2. Go to **Templates** tab
3. Click on **Email address verification**
4. Customize the template:
   - **From name**: ConnectFlow
   - **Reply-to email**: your-email@yourdomain.com (or leave default)
   - **Subject**: Verify your email for ConnectFlow
   - **Email body**: Customize the message

5. Click **SAVE**

---

### 3. Authorize Your Domain

**Steps:**
1. In Firebase Console → **Authentication**
2. Go to **Settings** tab
3. Scroll to **Authorized domains**
4. Make sure these domains are listed:
   - `localhost` (for development)
   - `connectflowpro-f1202.firebaseapp.com` (default)
   - Your custom domain (if you have one, e.g., `connectflow.onrender.com`)

5. Click **Add domain** if missing, then add:
   ```
   <your-app-name>.onrender.com
   ```

---

### 4. Check SMTP Settings (Advanced)

Firebase uses its own email service, but you can customize:

**Steps:**
1. Firebase Console → **Authentication** → **Templates**
2. At bottom, look for **SMTP settings** (if available)
3. Or use Firebase's default email service (recommended for now)

**Note:** For production, you might want to use:
- SendGrid
- AWS SES  
- Mailgun

---

### 5. Test Email Verification

**Test Steps:**
1. Sign up with a real email address (not a fake one)
2. Check spam/junk folder
3. Wait 2-3 minutes (emails can be delayed)
4. Check Firebase Console → **Authentication** → **Users**
   - User should appear in the list
   - Email column should show the email address

---

### 6. Check Firebase Logs

**Steps:**
1. Firebase Console → **Stackdriver** (or **Cloud Logging**)
2. Look for email-related errors
3. Filter by `authentication` service

---

## 🐛 Common Issues & Fixes

### Issue 1: "Email not verified" but email never sent

**Cause:** Firebase email templates not configured or provider not enabled

**Fix:**
1. Enable Email/Password provider (see Step 1)
2. Configure email templates (see Step 2)

---

### Issue 2: Emails go to spam

**Cause:** Firebase default sender reputation

**Fix:**
1. Use custom SMTP with verified domain
2. Or wait for Firebase to whitelist (takes time)
3. Tell users to check spam folder
4. Add to email template: "Add us to your contacts"

---

### Issue 3: "auth/invalid-continue-uri"

**Cause:** Domain not authorized

**Fix:**
- Add your Render domain to authorized domains (see Step 3)

---

### Issue 4: Users never receive email

**Cause:** Multiple possibilities

**Fixes to try:**
1. **Check user's email address** - Make sure it's valid
2. **Check spam folder** - Firebase emails often land here
3. **Wait 5-10 minutes** - Email delivery can be delayed
4. **Try different email** - Some providers block Firebase emails
5. **Check Firebase quota** - Free tier has limits

---

## 🔧 Quick Fix for Production

### Option A: Manual Verification (Temporary)

As super admin, you can manually verify users in Firebase Console:

1. Go to Firebase Console → **Authentication** → **Users**
2. Find the user
3. Click on the user
4. Manually mark email as verified (if option available)

---

### Option B: Custom Email Service (Recommended for Production)

Integrate a proper email service:

1. **SendGrid** (Free tier: 100 emails/day)
2. **AWS SES** (Free tier: 62,000 emails/month)
3. **Mailgun** (Free tier: 5,000 emails/month)

Let me know if you want me to implement this!

---

## 📋 Immediate Actions

**DO THIS NOW:**

1. ✅ Go to Firebase Console
2. ✅ Check **Authentication** → **Sign-in method**
3. ✅ Make sure **Email/Password** is ENABLED
4. ✅ Go to **Templates** tab
5. ✅ Configure **Email address verification** template
6. ✅ Go to **Settings** tab
7. ✅ Add your Render domain to **Authorized domains**

**Then test:**
1. Sign up with a NEW email
2. Check spam/inbox
3. Wait 2-3 minutes

---

## 🆘 Still Not Working?

**Share this info:**
1. Screenshot of Firebase Console → Authentication → Sign-in method
2. Screenshot of Firebase Console → Authentication → Templates
3. Screenshot of Firebase Console → Authentication → Settings → Authorized domains
4. Any error messages in browser console (F12)
5. Test user email address you're trying

Then I can help debug further!

---

**Last Updated:** January 1, 2026

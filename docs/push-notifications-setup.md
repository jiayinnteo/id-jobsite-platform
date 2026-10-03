# Push Notifications — Firebase (FCM) Setup Walkthrough

The platform already has the full push plumbing built:
- **Backend** stores device tokens and fans notifications out to them via an FCM
  adapter (mock when unconfigured).
- **Mobile** captures the device's FCM token on sign-in, registers it, refreshes
  it, and unregisters on sign-out.

Until you complete the steps below, push runs in **mock/no-op mode**: the app
works normally and in-app notifications still appear, but no lock-screen pushes
are delivered. Follow this guide to turn real push on.

---

## 1. Create a Firebase project

1. Go to the [Firebase console](https://console.firebase.google.com/) and
   **Add project** (you can link it to an existing Google Cloud project).
2. In the project, open **Build → Cloud Messaging** and make sure the
   **Firebase Cloud Messaging API (V1)** is enabled.

## 2. Add your mobile apps to the project

### Android
1. In Firebase: **Project settings → Your apps → Add app → Android**.
2. Use the app's **package name** (the `applicationId` in
   `mobile/android/app/build.gradle`).
3. Download **`google-services.json`** and place it at:
   ```
   mobile/android/app/google-services.json
   ```
4. Ensure the Google Services Gradle plugin is applied (standard FlutterFire
   setup) — `flutterfire configure` does this for you (see step 4).

### iOS
1. In Firebase: **Add app → iOS**, using the app's **bundle ID**
   (`mobile/ios/Runner.xcodeproj` → `PRODUCT_BUNDLE_IDENTIFIER`).
2. Download **`GoogleService-Info.plist`** and add it to
   `mobile/ios/Runner/` (via Xcode so it's included in the target).
3. In Firebase **Cloud Messaging → Apple app config**, upload an **APNs
   authentication key** (`.p8`) from your Apple Developer account.

> Tip: the easiest path is the FlutterFire CLI — see step 4 — which generates the
> native config and a `firebase_options.dart` for you.

## 3. (Recommended) Run the FlutterFire CLI

```bash
dart pub global activate flutterfire_cli
cd mobile
flutterfire configure
```

Select your Firebase project and the Android/iOS apps. This writes the native
config files and `lib/firebase_options.dart`. If you use it, update
`PushService.start()` to initialize with those options:

```dart
await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
```

(Without it, `Firebase.initializeApp()` reads the native config files directly.)

## 4. Configure the backend

Create a **service account** for sending messages:

1. Firebase console → **Project settings → Service accounts → Generate new
   private key**. This downloads a JSON file.
2. Set backend env (see `backend/.env.example`):
   ```env
   FCM_ENABLED=true
   FCM_PROJECT_ID=your-firebase-project-id
   # Either a path mounted into the container, or the JSON contents inline:
   FCM_SERVICE_ACCOUNT=/run/secrets/firebase-service-account.json
   ```
3. Keep the key **out of git** — mount it as a secret / env var in your deploy.

The backend uses the FCM **HTTP v1** API; `google-auth` (already a dependency)
mints the access token from the service account.

## 5. Verify

1. Start the backend with the env above; `GET /health` should report
   `"push_enabled": true`.
2. Run the app on a real device (push does not work on iOS simulators), sign in,
   and accept the notification permission prompt.
3. The app calls `POST /devices/register` with the FCM token (visible in the
   backend logs / `device_tokens` table).
4. Trigger a notifiable action (e.g. assign a defect, propose a material). The
   target user's device should receive a push.

## How it behaves

- Each notifiable event creates an in-app notification **and** pushes to every
  registered device of each recipient.
- Tokens FCM reports as unregistered/invalid are **pruned automatically**.
- Signing out calls `POST /devices/unregister` so the device stops receiving
  that user's pushes.

## Security notes

- Never commit `google-services.json`, `GoogleService-Info.plist`, or the
  service-account JSON. Treat the service account as a secret.
- The service account only needs the Cloud Messaging scope.

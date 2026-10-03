# Mobile — ID Job-Site Platform (Flutter)

## Run

```bash
cd mobile
flutter pub get
# Point at your backend (Android emulator reaches host via 10.0.2.2):
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

## Tests & analysis

```bash
flutter analyze
flutter test
```

## Push notifications (optional — needs a Firebase project)

The app registers a device push token with the backend after sign-in and
unregisters on sign-out. Until Firebase is configured, this runs in a safe
no-op mode (the app still works; no real pushes are delivered).

To enable real push:
1. Create a **Firebase project** and add Android/iOS apps to it.
2. Add the native config files:
   - Android: `android/app/google-services.json`
   - iOS: `ios/Runner/GoogleService-Info.plist` (plus APNs key in Firebase).
3. On the **backend**, set `FCM_ENABLED=true`, `FCM_PROJECT_ID`, and
   `FCM_SERVICE_ACCOUNT` (path to or contents of a Firebase service-account JSON).

Once configured, notifications fan out to each user's registered devices and
dead tokens are pruned automatically.

**Full step-by-step guide:** [`docs/push-notifications-setup.md`](../docs/push-notifications-setup.md).

# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in /usr/local/Cellar/android-sdk/24.3.3/tools/proguard/proguard-android.txt

# Keep React Native classes
-keep class com.facebook.react.** { *; }

# Keep Kotlin
-keep class kotlin.** { *; }
-keep class org.jetbrains.** { *; }

# Keep native methods
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

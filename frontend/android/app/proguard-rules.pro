# ML Kit text recognition: we only bundle the Latin-script model. The Flutter
# plugin also references the optional CJK/Devanagari recognizers — suppress the
# missing-class errors for those unbundled variants (they are never invoked).
-dontwarn com.google.mlkit.vision.text.chinese.**
-dontwarn com.google.mlkit.vision.text.devanagari.**
-dontwarn com.google.mlkit.vision.text.japanese.**
-dontwarn com.google.mlkit.vision.text.korean.**

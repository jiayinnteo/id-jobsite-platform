import 'package:flutter/material.dart';

/// Parses a #RRGGBB / #AARRGGBB hex string into a Color, or null.
Color? colourFromHex(String? hex) {
  if (hex == null) return null;
  var h = hex.replaceAll('#', '').trim();
  if (h.length == 6) h = 'FF$h';
  if (h.length != 8) return null;
  final value = int.tryParse(h, radix: 16);
  return value == null ? null : Color(value);
}

/// A rounded colour swatch; falls back to a neutral tile when no colour.
class ColourSwatch extends StatelessWidget {
  const ColourSwatch({super.key, this.hex, this.size = 40});
  final String? hex;
  final double size;

  @override
  Widget build(BuildContext context) {
    final colour = colourFromHex(hex);
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: colour ?? Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.black.withValues(alpha: 0.1)),
      ),
      child: colour == null
          ? const Icon(Icons.palette_outlined, size: 18)
          : null,
    );
  }
}

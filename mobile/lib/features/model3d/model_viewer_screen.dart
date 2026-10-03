import 'package:flutter/material.dart';
import 'package:model_viewer_plus/model_viewer_plus.dart';

import '../../widgets/colour_swatch.dart';
import '../../widgets/states.dart';

/// A surface→material mapping applied to the 3D model for preview.
/// Uses a tiled [swatchUrl] texture when available, else a flat [colourHex].
class SurfacePreview {
  const SurfacePreview({
    required this.surface,
    required this.colourHex,
    this.swatchUrl,
    this.label,
  });
  final String surface;
  final String? colourHex;
  final String? swatchUrl;
  final String? label;
}

/// Converts a #RRGGBB hex to normalized RGBA (0..1) for model-viewer's
/// setBaseColorFactor. Returns null if unparseable.
List<double>? _rgbaFactor(String? hex) {
  final c = colourFromHex(hex);
  if (c == null) return null;
  // ignore: deprecated_member_use
  return [c.red / 255.0, c.green / 255.0, c.blue / 255.0, 1.0];
}

/// Builds JS (run inside <model-viewer>) that recolours named materials once
/// the model loads. Matching is case-insensitive and also matches by substring
/// so "floor" maps to a material named "Floor_Wood_01".
String _previewJs(List<SurfacePreview> previews) {
  final entries = <String>[];
  for (final p in previews) {
    final surface = p.surface.replaceAll("'", "").toLowerCase();
    if (surface.isEmpty) continue;
    final rgba = _rgbaFactor(p.colourHex);
    final tex = (p.swatchUrl != null && p.swatchUrl!.startsWith('http'))
        ? "'${p.swatchUrl!.replaceAll("'", "")}'"
        : 'null';
    final colour = rgba != null ? '[${rgba.join(',')}]' : 'null';
    entries.add("{s:'$surface',c:$colour,t:$tex}");
  }
  if (entries.isEmpty) return '';
  return '''
const mv = document.querySelector('model-viewer');
async function applyPreview() {
  const map = [${entries.join(',')}];
  if (!mv.model) return;
  for (const mat of mv.model.materials) {
    const name = (mat.name || '').toLowerCase();
    for (const m of map) {
      if (name !== m.s && !name.includes(m.s)) continue;
      try {
        if (m.t) {
          // Photorealistic preview: tile the material swatch image.
          const texture = await mv.createTexture(m.t);
          mat.pbrMetallicRoughness.baseColorTexture.setTexture(texture);
          if (m.c) mat.pbrMetallicRoughness.setBaseColorFactor([1,1,1,1]);
        } else if (m.c) {
          // Fallback: flat base colour (paints / solid finishes).
          mat.pbrMetallicRoughness.setBaseColorFactor(m.c);
        }
      } catch (e) {}
    }
  }
}
mv.addEventListener('load', applyPreview);
if (mv.loaded) applyPreview();
''';
}

/// The 3D viewer body (no Scaffold) so it can be embedded in a tab.
/// When [previews] are supplied and [previewOn] is true, selected material
/// colours are applied to the matching model surfaces.
class ModelViewerBody extends StatelessWidget {
  const ModelViewerBody({
    super.key,
    required this.modelUrl,
    this.title,
    this.previews = const [],
    this.previewOn = true,
  });

  final String? modelUrl;
  final String? title;
  final List<SurfacePreview> previews;
  final bool previewOn;

  @override
  Widget build(BuildContext context) {
    if (modelUrl == null || modelUrl!.startsWith('mock://')) {
      return const EmptyState(
        icon: Icons.view_in_ar_outlined,
        title: 'No 3D model yet',
        message:
            'Your designer can upload a 3D model (glTF/GLB) exported from '
            'SketchUp. It will appear here to orbit and zoom.',
      );
    }
    final js = previewOn ? _previewJs(previews) : '';
    return ModelViewer(
      // Rebuild the webview when the preview script changes.
      key: ValueKey('mv_${modelUrl}_${js.hashCode}'),
      src: modelUrl!,
      alt: title ?? '3D model of your renovation',
      ar: false,
      autoRotate: true,
      cameraControls: true,
      disableZoom: false,
      backgroundColor: Theme.of(context).colorScheme.surface,
      relatedJs: js.isEmpty ? null : js,
    );
  }
}

/// Full-screen 3D viewer (e.g. when opened from a deep link).
/// Full 3D authoring is intentionally out of scope (Requirement 18.5).
class ModelViewerScreen extends StatelessWidget {
  const ModelViewerScreen({
    super.key,
    required this.modelUrl,
    this.title,
    this.previews = const [],
  });

  final String? modelUrl;
  final String? title;
  final List<SurfacePreview> previews;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title ?? '3D view')),
      body: ModelViewerBody(
        modelUrl: modelUrl,
        title: title,
        previews: previews,
      ),
    );
  }
}

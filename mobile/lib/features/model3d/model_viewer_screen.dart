import 'package:flutter/material.dart';
import 'package:model_viewer_plus/model_viewer_plus.dart';

import '../../widgets/states.dart';

/// The 3D viewer body (no Scaffold) so it can be embedded in a tab.
class ModelViewerBody extends StatelessWidget {
  const ModelViewerBody({super.key, required this.modelUrl, this.title});

  final String? modelUrl;
  final String? title;

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
    return ModelViewer(
      src: modelUrl!,
      alt: title ?? '3D model of your renovation',
      ar: false,
      autoRotate: true,
      cameraControls: true,
      disableZoom: false,
      backgroundColor: Theme.of(context).colorScheme.surface,
    );
  }
}

/// Full-screen 3D viewer (e.g. when opened from a deep link).
/// Full 3D authoring is intentionally out of scope (Requirement 18.5).
class ModelViewerScreen extends StatelessWidget {
  const ModelViewerScreen({super.key, required this.modelUrl, this.title});

  final String? modelUrl;
  final String? title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title ?? '3D view')),
      body: ModelViewerBody(modelUrl: modelUrl, title: title),
    );
  }
}

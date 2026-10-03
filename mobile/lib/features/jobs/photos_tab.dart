import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../data/jobs_repository.dart';
import '../../widgets/states.dart';
import 'jobs_providers.dart';

/// Shared site-photo gallery. Any job member can capture or pick a photo and
/// upload it; everyone on the job sees it.
class PhotosTab extends ConsumerStatefulWidget {
  const PhotosTab({super.key, required this.jobId, this.defectId});
  final String jobId;
  final String? defectId;

  @override
  ConsumerState<PhotosTab> createState() => _PhotosTabState();
}

class _PhotosTabState extends ConsumerState<PhotosTab> {
  bool _uploading = false;

  Future<void> _addPhoto(ImageSource source) async {
    final picker = ImagePicker();
    final file = await picker.pickImage(source: source, imageQuality: 85);
    if (file == null) return;

    setState(() => _uploading = true);
    try {
      final bytes = await file.readAsBytes();
      final repo = ref.read(jobsRepositoryProvider);
      final target = await repo.createPhoto(
        widget.jobId,
        filename: file.name,
        mimeType: file.mimeType ?? 'image/jpeg',
        sizeBytes: bytes.length,
        defectId: widget.defectId,
      );
      await repo.uploadToPresignedUrl(
        target['upload_url'] as String,
        bytes,
        file.mimeType ?? 'image/jpeg',
      );
      ref.invalidate(photosProvider(widget.jobId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo uploaded.')),
        );
      }
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Upload failed — please try again.')),
        );
      }
    } finally {
      if (mounted) setState(() => _uploading = false);
    }
  }

  void _pickSource() {
    showModalBottomSheet(
      context: context,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.photo_camera_outlined),
              title: const Text('Take a photo'),
              onTap: () {
                Navigator.pop(context);
                _addPhoto(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Choose from gallery'),
              onTap: () {
                Navigator.pop(context);
                _addPhoto(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final photos = ref.watch(photosProvider(widget.jobId));
    return Scaffold(
      body: photos.when(
        loading: () => const LoadingState(),
        error: (_, __) => const EmptyState(
          icon: Icons.wifi_off_rounded,
          title: 'Could not load photos',
        ),
        data: (items) {
          if (items.isEmpty) {
            return const EmptyState(
              icon: Icons.photo_camera_outlined,
              title: 'No photos yet',
              message: 'Capture the site so everyone can see its current state.',
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(photosProvider(widget.jobId)),
            child: GridView.builder(
              padding: const EdgeInsets.all(8),
              gridDelegate:
                  const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3,
                mainAxisSpacing: 6,
                crossAxisSpacing: 6,
              ),
              itemCount: items.length,
              itemBuilder: (context, i) {
                final p = items[i];
                return ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: p.downloadUrl != null &&
                          !p.downloadUrl!.startsWith('mock://')
                      ? Image.network(p.downloadUrl!, fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => const _PhotoPlaceholder())
                      : const _PhotoPlaceholder(),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _uploading ? null : _pickSource,
        icon: _uploading
            ? const SizedBox(
                width: 18, height: 18,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.add_a_photo_outlined),
        label: const Text('Add photo'),
      ),
    );
  }
}

class _PhotoPlaceholder extends StatelessWidget {
  const _PhotoPlaceholder();
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).colorScheme.secondaryContainer,
      child: const Center(child: Icon(Icons.image_outlined)),
    );
  }
}

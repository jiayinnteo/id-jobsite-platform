import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/user_role.dart';
import '../../data/materials_repository.dart';
import '../../data/models.dart';
import '../../widgets/app_button.dart';
import '../../widgets/colour_swatch.dart';
import '../../widgets/states.dart';
import '../auth/auth_controller.dart';
import 'catalogue_screen.dart';

final materialSelectionsProvider = FutureProvider.autoDispose
    .family<List<MaterialSelection>, String>((ref, jobId) async {
  return ref.read(materialsRepositoryProvider).selections(jobId);
});

/// Per-job materials & finishes. IDs add selections from supplier catalogues;
/// clients approve or request a change.
class MaterialsTab extends ConsumerWidget {
  const MaterialsTab({super.key, required this.jobId});
  final String jobId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authControllerProvider).valueOrNull;
    final role = auth is AuthSignedIn ? auth.role : null;
    final isFirm = role == UserRole.id || role == UserRole.idBoss;
    final isClient = role == UserRole.client;
    final selections = ref.watch(materialSelectionsProvider(jobId));

    return Scaffold(
      body: selections.when(
        loading: () => const LoadingState(),
        error: (_, __) => const EmptyState(
          icon: Icons.wifi_off_rounded,
          title: 'Could not load materials',
        ),
        data: (items) {
          if (items.isEmpty) {
            return EmptyState(
              icon: Icons.palette_outlined,
              title: 'No materials selected yet',
              message: isFirm
                  ? 'Add laminates, tiles, paints and more from supplier catalogues.'
                  : 'Your designer will add material selections here to review.',
            );
          }
          return RefreshIndicator(
            onRefresh: () async =>
                ref.invalidate(materialSelectionsProvider(jobId)),
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: items.length,
              itemBuilder: (context, i) => _SelectionCard(
                jobId: jobId,
                selection: items[i],
                canDecide: isClient,
                canMapSurface: isFirm,
              ),
            ),
          );
        },
      ),
      floatingActionButton: isFirm
          ? FloatingActionButton.extended(
              onPressed: () => _addSelection(context, ref),
              icon: const Icon(Icons.add),
              label: const Text('Add material'),
            )
          : null,
    );
  }

  Future<void> _addSelection(BuildContext context, WidgetRef ref) async {
    final product = await Navigator.of(context).push<MaterialProduct>(
      MaterialPageRoute(builder: (_) => const CatalogueScreen()),
    );
    if (product == null || !context.mounted) return;

    final areaCtrl = TextEditingController();
    final confirmed = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => Padding(
        padding: EdgeInsets.fromLTRB(
          24, 8, 24, 24 + MediaQuery.of(context).viewInsets.bottom,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ColourSwatch(hex: product.colourHex),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(product.name,
                          style: const TextStyle(fontWeight: FontWeight.w700)),
                      if (product.colour != null) Text(product.colour!),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: areaCtrl,
              decoration: const InputDecoration(
                labelText: 'Where will it be used? (e.g. Living room floor)',
              ),
            ),
            const SizedBox(height: 16),
            AppButton(
              label: 'Propose to client',
              icon: Icons.send_rounded,
              onPressed: () => Navigator.pop(context, true),
            ),
          ],
        ),
      ),
    );

    if (confirmed == true) {
      await ref.read(materialsRepositoryProvider).addSelection(
            jobId,
            productId: product.id,
            category: product.category,
            area: areaCtrl.text.trim().isEmpty ? null : areaCtrl.text.trim(),
            colour: product.colour,
            colourHex: product.colourHex,
          );
      ref.invalidate(materialSelectionsProvider(jobId));
    }
  }
}

class _SelectionCard extends ConsumerWidget {
  const _SelectionCard({
    required this.jobId,
    required this.selection,
    required this.canDecide,
    this.canMapSurface = false,
  });
  final String jobId;
  final MaterialSelection selection;
  final bool canDecide;
  final bool canMapSurface;

  Color _statusColor(BuildContext context) {
    switch (selection.status) {
      case 'APPROVED':
        return Colors.green;
      case 'CHANGE_REQUESTED':
        return Theme.of(context).colorScheme.error;
      default:
        return Theme.of(context).colorScheme.secondary;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = selection;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                ColourSwatch(hex: s.colourHex, size: 48),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${s.category[0]}${s.category.substring(1).toLowerCase()}'
                        '${s.colour != null ? ' · ${s.colour}' : ''}',
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      if (s.area != null) Text(s.area!),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _statusColor(context).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    s.status.replaceAll('_', ' '),
                    style: TextStyle(
                      color: _statusColor(context),
                      fontWeight: FontWeight.w700,
                      fontSize: 11,
                    ),
                  ),
                ),
              ],
            ),
            if (canMapSurface) ...[
              const SizedBox(height: 8),
              InkWell(
                onTap: () => _mapSurface(context, ref),
                child: Row(
                  children: [
                    const Icon(Icons.view_in_ar_outlined, size: 16),
                    const SizedBox(width: 6),
                    Text(
                      s.modelSurface == null
                          ? 'Map to a 3D surface for preview'
                          : '3D surface: ${s.modelSurface}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(width: 4),
                    const Icon(Icons.edit_outlined, size: 14),
                  ],
                ),
              ),
            ],
            if (canDecide && s.status == 'PROPOSED') ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: AppButton(
                      label: 'Request change',
                      kind: AppButtonKind.secondary,
                      onPressed: () => _decide(ref, approve: false),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: AppButton(
                      label: 'Approve',
                      icon: Icons.check_rounded,
                      onPressed: () => _decide(ref, approve: true),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _decide(WidgetRef ref, {required bool approve}) async {
    await ref
        .read(materialsRepositoryProvider)
        .decideSelection(selection.id, approve: approve);
    ref.invalidate(materialSelectionsProvider(jobId));
  }

  Future<void> _mapSurface(BuildContext context, WidgetRef ref) async {
    final ctrl = TextEditingController(text: selection.modelSurface ?? '');
    final surface = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: const Text('Map to 3D surface'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter the material/mesh name in the 3D model this finish '
              'applies to (e.g. "floor", "wall_living"). Matching is '
              'case-insensitive.',
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              autofocus: true,
              decoration: const InputDecoration(hintText: 'floor'),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          AppButton(
            label: 'Save',
            onPressed: () => Navigator.pop(context, ctrl.text.trim()),
          ),
        ],
      ),
    );
    if (surface != null && surface.isNotEmpty) {
      await ref
          .read(materialsRepositoryProvider)
          .mapSurface(selection.id, surface);
      ref.invalidate(materialSelectionsProvider(jobId));
    }
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../data/materials_repository.dart';
import '../../data/models.dart';
import '../../widgets/colour_swatch.dart';
import '../../widgets/states.dart';

const kCategories = [
  'LAMINATE', 'TILE', 'WORKTOP', 'PAINT', 'VINYL', 'FLOORING', 'OTHER',
];

final _productsProvider = FutureProvider.autoDispose
    .family<List<MaterialProduct>, String>((ref, category) async {
  return ref.read(materialsRepositoryProvider).products(category: category);
});

/// Browse supplier catalogues (SG/MY). Returns the chosen product when tapped.
class CatalogueScreen extends ConsumerStatefulWidget {
  const CatalogueScreen({super.key, this.initialCategory = 'LAMINATE'});
  final String initialCategory;

  @override
  ConsumerState<CatalogueScreen> createState() => _CatalogueScreenState();
}

class _CatalogueScreenState extends ConsumerState<CatalogueScreen> {
  late String _category = widget.initialCategory;

  @override
  Widget build(BuildContext context) {
    final products = ref.watch(_productsProvider(_category));
    return Scaffold(
      appBar: AppBar(
        title: const Text('Material catalogue'),
        actions: [
          IconButton(
            tooltip: 'Refresh catalogue',
            icon: const Icon(Icons.sync),
            onPressed: () async {
              await ref.read(materialsRepositoryProvider).syncCatalogues();
              ref.invalidate(_productsProvider(_category));
            },
          ),
        ],
      ),
      body: Column(
        children: [
          SizedBox(
            height: 56,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              children: [
                for (final c in kCategories)
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: Text(c[0] + c.substring(1).toLowerCase()),
                      selected: _category == c,
                      onSelected: (_) => setState(() => _category = c),
                    ),
                  ),
              ],
            ),
          ),
          Expanded(
            child: products.when(
              loading: () => const LoadingState(),
              error: (_, __) => const EmptyState(
                icon: Icons.wifi_off_rounded,
                title: 'Could not load catalogue',
                message: 'Tap the sync icon to import supplier catalogues.',
              ),
              data: (items) {
                if (items.isEmpty) {
                  return const EmptyState(
                    icon: Icons.inventory_2_outlined,
                    title: 'No products in this category',
                    message: 'Tap the sync icon to import supplier catalogues.',
                  );
                }
                return ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: items.length,
                  itemBuilder: (context, i) {
                    final p = items[i];
                    return Card(
                      child: ListTile(
                        leading: ColourSwatch(hex: p.colourHex),
                        title: Text(
                          p.name,
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        subtitle: Text([
                          if (p.colour != null) p.colour,
                          if (p.finish != null) p.finish,
                          if (p.productCode != null) p.productCode,
                        ].whereType<String>().join(' · ')),
                        trailing: p.sourceUrl != null
                            ? IconButton(
                                icon: const Icon(Icons.open_in_new, size: 18),
                                tooltip: 'View on supplier site',
                                onPressed: () => launchUrl(
                                  Uri.parse(p.sourceUrl!),
                                  mode: LaunchMode.externalApplication,
                                ),
                              )
                            : null,
                        onTap: () => Navigator.of(context).pop(p),
                      ),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';
import 'models.dart';

final materialsRepositoryProvider = Provider(
  (ref) => MaterialsRepository(ref.read(apiClientProvider)),
);

/// Supplier catalogue + per-job material selections.
class MaterialsRepository {
  MaterialsRepository(this._dio);
  final Dio _dio;

  Future<List<MaterialProduct>> products({String? category}) async {
    final res = await _dio.get('/materials/products', queryParameters: {
      if (category != null) 'category': category,
    });
    return (res.data as List)
        .map((e) => MaterialProduct.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<Map<String, dynamic>>> suppliers() async {
    final res = await _dio.get('/materials/suppliers');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  Future<void> syncCatalogues() async {
    await _dio.post('/materials/sync');
  }

  Future<List<MaterialSelection>> selections(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/materials');
    return (res.data as List)
        .map((e) => MaterialSelection.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> addSelection(
    String jobId, {
    String? productId,
    required String category,
    String? area,
    String? colour,
    String? colourHex,
    String? note,
  }) async {
    await _dio.post('/jobs/$jobId/materials', data: {
      'product_id': productId,
      'category': category,
      'area': area,
      'colour': colour,
      'colour_hex': colourHex,
      'note': note,
    });
  }

  Future<void> decideSelection(
    String selectionId, {
    required bool approve,
    String? note,
  }) async {
    await _dio.post('/material-selections/$selectionId/decision', data: {
      'approve': approve,
      'note': note,
    });
  }
}

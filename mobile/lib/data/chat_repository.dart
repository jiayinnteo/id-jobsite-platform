import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_client.dart';

final chatRepositoryProvider = Provider(
  (ref) => ChatRepository(ref.read(apiClientProvider)),
);

/// In-app chat + AI drafts + notifications + Google Calendar status.
class ChatRepository {
  ChatRepository(this._dio);
  final Dio _dio;

  Future<Map<String, dynamic>> conversationForJob(String jobId) async {
    final res = await _dio.get('/jobs/$jobId/conversation');
    return res.data as Map<String, dynamic>;
  }

  Future<List<Map<String, dynamic>>> messages(String conversationId) async {
    final res = await _dio.get('/conversations/$conversationId/messages');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> sendMessage(
    String conversationId,
    String body,
  ) async {
    final res = await _dio.post(
      '/conversations/$conversationId/messages',
      data: {'body': body},
    );
    return res.data as Map<String, dynamic>;
  }

  // --- AI drafts (human-in-the-loop) ---
  Future<List<Map<String, dynamic>>> pendingDrafts() async {
    final res = await _dio.get('/ai/drafts');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  Future<void> generateDraft(String conversationId) async {
    await _dio.post('/ai/drafts', data: {'conversation_id': conversationId});
  }

  Future<void> editDraft(String draftId, String text) async {
    await _dio.patch('/ai/drafts/$draftId', data: {'edited_text': text});
  }

  Future<void> approveDraft(String draftId) async {
    await _dio.post('/ai/drafts/$draftId/approve');
  }

  Future<void> rejectDraft(String draftId) async {
    await _dio.post('/ai/drafts/$draftId/reject');
  }

  // --- Notifications ---
  Future<List<Map<String, dynamic>>> notifications() async {
    final res = await _dio.get('/notifications');
    return (res.data as List).cast<Map<String, dynamic>>();
  }

  Future<int> unreadCount() async {
    final res = await _dio.get('/notifications/unread-count');
    return (res.data['unread'] as num).toInt();
  }

  Future<void> markRead(String id) async {
    await _dio.post('/notifications/$id/read');
  }

  // --- Google Calendar ---
  Future<Map<String, dynamic>> calendarStatus() async {
    final res = await _dio.get('/integrations/google/status');
    return res.data as Map<String, dynamic>;
  }

  Future<String?> calendarConnectUrl() async {
    final res = await _dio.post('/integrations/google/connect');
    return res.data['auth_url'] as String?;
  }

  Future<void> calendarDisconnect() async {
    await _dio.post('/integrations/google/disconnect');
  }
}

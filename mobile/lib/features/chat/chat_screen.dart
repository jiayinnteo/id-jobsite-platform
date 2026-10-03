import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../data/api_client.dart';
import '../../data/chat_repository.dart';
import '../../widgets/states.dart';

/// Conversation screen for a job's single conversation (in-app + WhatsApp
/// bridged). History newest-at-bottom; sending also mirrors to WhatsApp.
class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key, required this.conversationId});
  final String conversationId;

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _input = TextEditingController();
  final _scroll = ScrollController();
  List<Map<String, dynamic>> _messages = [];
  bool _loading = true;
  bool _sending = false;
  WebSocketChannel? _channel;

  @override
  void initState() {
    super.initState();
    _load();
    _connectLive();
  }

  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    _channel?.sink.close();
    super.dispose();
  }

  /// Subscribe to the conversation WebSocket for realtime message delivery.
  void _connectLive() {
    try {
      final base = kApiBaseUrl
          .replaceFirst('http://', 'ws://')
          .replaceFirst('https://', 'wss://')
          .replaceFirst('/api/v1', '');
      final uri = Uri.parse('$base/ws/conversations/${widget.conversationId}');
      _channel = WebSocketChannel.connect(uri);
      _channel!.stream.listen((event) {
        try {
          final msg = jsonDecode(event as String) as Map<String, dynamic>;
          if (_messages.any((m) => m['id'] == msg['id'])) return; // de-dup
          setState(() => _messages = [..._messages, msg]);
          _scrollToBottom();
        } catch (_) {/* ignore malformed frames */}
      }, onError: (_) {/* live updates are best-effort */});
    } catch (_) {/* fall back to REST-only */}
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.jumpTo(_scroll.position.maxScrollExtent);
      }
    });
  }

  Future<void> _load() async {
    try {
      final msgs = await ref
          .read(chatRepositoryProvider)
          .messages(widget.conversationId);
      if (mounted) setState(() => _messages = msgs);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _send() async {
    final text = _input.text.trim();
    if (text.isEmpty) return;
    setState(() => _sending = true);
    try {
      final msg = await ref
          .read(chatRepositoryProvider)
          .sendMessage(widget.conversationId, text);
      _input.clear();
      if (!_messages.any((m) => m['id'] == msg['id'])) {
        setState(() => _messages = [..._messages, msg]);
      }
      _scrollToBottom();
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Expanded(
          child: _loading
              ? const LoadingState()
              : _messages.isEmpty
                  ? const EmptyState(
                      icon: Icons.forum_outlined,
                      title: 'No messages yet',
                      message: 'Say hello — messages here also reach WhatsApp.',
                    )
                  : ListView.builder(
                      controller: _scroll,
                      padding: const EdgeInsets.all(12),
                      itemCount: _messages.length,
                      itemBuilder: (context, i) {
                        final m = _messages[i];
                        final outbound = m['direction'] == 'OUTBOUND';
                        final isWhatsApp = m['channel'] == 'WHATSAPP';
                        return Align(
                          alignment: outbound
                              ? Alignment.centerRight
                              : Alignment.centerLeft,
                          child: Container(
                            margin: const EdgeInsets.symmetric(vertical: 4),
                            padding: const EdgeInsets.all(12),
                            constraints: const BoxConstraints(maxWidth: 280),
                            decoration: BoxDecoration(
                              color: outbound
                                  ? scheme.primaryContainer
                                  : scheme.surfaceContainerHighest,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(m['body']?.toString() ?? ''),
                                if (isWhatsApp)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 4),
                                    child: Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(Icons.chat,
                                            size: 12, color: scheme.tertiary),
                                        const SizedBox(width: 4),
                                        Text('WhatsApp',
                                            style: TextStyle(
                                                fontSize: 11,
                                                color: scheme.tertiary)),
                                      ],
                                    ),
                                  ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _input,
                    minLines: 1,
                    maxLines: 4,
                    decoration: const InputDecoration(
                      hintText: 'Type a message…',
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: _sending ? null : _send,
                  icon: const Icon(Icons.send_rounded),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

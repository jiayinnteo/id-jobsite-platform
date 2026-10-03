import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/user_role.dart';
import '../../data/auth_repository.dart';

/// Authentication session state.
sealed class AuthState {
  const AuthState();
}

class AuthUnknown extends AuthState {
  const AuthUnknown();
}

class AuthSignedOut extends AuthState {
  const AuthSignedOut();
}

class AuthSignedIn extends AuthState {
  const AuthSignedIn(this.role);
  final UserRole role;
}

final authControllerProvider =
    AsyncNotifierProvider<AuthController, AuthState>(AuthController.new);

class AuthController extends AsyncNotifier<AuthState> {
  AuthRepository get _repo => ref.read(authRepositoryProvider);

  @override
  Future<AuthState> build() async {
    final role = await _repo.currentRole();
    return role == null ? const AuthSignedOut() : AuthSignedIn(role);
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.login(email, password);
      final role = await _repo.currentRole();
      return role == null ? const AuthSignedOut() : AuthSignedIn(role);
    });
  }

  Future<void> register({
    required String email,
    required String password,
    required String fullName,
    required UserRole role,
    String? phone,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.register(
        email: email,
        password: password,
        fullName: fullName,
        role: role,
        phone: phone,
      );
      final current = await _repo.currentRole();
      return current == null ? const AuthSignedOut() : AuthSignedIn(current);
    });
  }

  Future<void> logout() async {
    await _repo.logout();
    state = const AsyncData(AuthSignedOut());
  }
}

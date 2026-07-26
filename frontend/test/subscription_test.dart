import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:electronics_scanner/models/entitlement.dart';
import 'package:electronics_scanner/services/payment_service.dart';
import 'package:electronics_scanner/services/subscription_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('Entitlement', () {
    test('is active while unexpired and lapses afterwards', () {
      final live = Entitlement(
        premium: true,
        expiresAt: DateTime.now().add(const Duration(days: 3)),
      );
      final lapsed = Entitlement(
        premium: true,
        expiresAt: DateTime.now().subtract(const Duration(minutes: 1)),
      );
      expect(live.isActive, isTrue);
      expect(lapsed.isActive, isFalse);
      expect(Entitlement.none.isActive, isFalse);
    });

    test('a plan with no expiry is lifetime', () {
      const lifetime = Entitlement(premium: true, planName: 'Pro Lifetime');
      expect(lifetime.isActive, isTrue);
      expect(lifetime.isLifetime, isTrue);
      expect(lifetime.daysRemaining, isNull);
    });

    test('parses the payment backend document', () {
      final entitlement = Entitlement.fromMap({
        'premium': true,
        'plan': 'monthly',
        'planName': 'Pro Monthly',
        'source': 'gcash',
        'expiresAt': '2099-01-31T10:00:00Z',
      });
      expect(entitlement.premium, isTrue);
      expect(entitlement.plan, 'monthly');
      expect(entitlement.source, 'gcash');
      expect(entitlement.expiresAt!.year, 2099);
      expect(entitlement.isActive, isTrue);
    });
  });

  group('SubscriptionService', () {
    setUp(() => SharedPreferences.setMockInitialValues({}));

    test('a paid subscription unlocks Pro and survives a restart', () async {
      final service = SubscriptionService();
      await service.load();
      expect(service.isPremium, isFalse);

      await service.setEntitlement(Entitlement(
        premium: true,
        planName: 'Pro Monthly',
        source: 'gcash',
        expiresAt: DateTime.now().add(const Duration(days: 30)),
      ));
      expect(service.isPremium, isTrue);
      expect(service.planName, 'Pro Monthly');

      final restarted = SubscriptionService();
      await restarted.load();
      expect(restarted.isPremium, isTrue);
      expect(restarted.premiumUntil, isNotNull);
    });

    test('an expired subscription drops back to the free tier offline',
        () async {
      final service = SubscriptionService();
      await service.load();
      await service.setEntitlement(Entitlement(
        premium: true,
        expiresAt: DateTime.now().subtract(const Duration(days: 1)),
      ));
      expect(service.isPremium, isFalse);
      expect(service.canScan, isTrue); // free scans still available
    });

    test('free scans are capped, Pro is not', () async {
      final service = SubscriptionService();
      await service.load();
      for (var i = 0; i < 20; i++) {
        await service.recordScan();
      }
      expect(service.freeScansRemaining, 0);
      expect(service.canScan, isFalse);

      await service.setPremium(true);
      expect(service.canScan, isTrue);
    });
  });

  group('PaymentPlan', () {
    test('reads the backend plan payload', () {
      final plan = PaymentPlan.fromJson({
        'id': 'yearly',
        'name': 'Pro Yearly',
        'price': 1499,
        'currency': 'PHP',
        'days': 365,
        'badge': 'Best value',
        'display_price': '₱1,499/yr',
      });
      expect(plan.priceLabel, '₱1,499/yr');
      expect(plan.lengthLabel, '12 months of Pro');
    });

    test('a plan without days is lifetime', () {
      final plan = PaymentPlan.fromJson(
          {'id': 'lifetime', 'name': 'Pro Lifetime', 'price': 2999});
      expect(plan.days, isNull);
      expect(plan.lengthLabel, 'Lifetime access');
      expect(plan.priceLabel, '₱2999');
    });
  });

  group('PaymentStatus', () {
    test('flags the three outcomes the app reacts to', () {
      expect(PaymentStatus.fromJson({'status': 'paid', 'premium': true}).isPaid,
          isTrue);
      expect(PaymentStatus.fromJson({'status': 'pending'}).isPending, isTrue);
      expect(PaymentStatus.fromJson({'status': 'expired'}).isFailed, isTrue);
    });
  });
}

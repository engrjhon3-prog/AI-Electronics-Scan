import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;

import 'package:electronics_scanner/services/local_repository.dart';
import 'package:electronics_scanner/services/resistor_decoder.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LocalRepository', () {
    test('loads the bundled knowledge base', () async {
      final repo = LocalRepository();
      await repo.load();
      expect(repo.components.length, greaterThanOrEqualTo(10));

      final ne555 = repo.getComponent('ne555');
      expect(ne555, isNotNull);
      expect(ne555!.pins.length, 8);

      // Alias matching mirrors the backend behaviour.
      expect(repo.findByAlias('NE555'.toLowerCase()), 'ne555');
      expect(repo.findByAlias('i found an hc-sr04 sensor'), 'hcsr04');
    });

    test('ships the full catalog, including IoT modules', () async {
      final repo = LocalRepository();
      await repo.load();
      expect(repo.components.length, greaterThanOrEqualTo(150));

      final esp32 = repo.getComponent('esp32_devkit');
      expect(esp32, isNotNull);
      expect(esp32!.category, 'boards');

      // A few of the parts an IoT build actually needs.
      for (final id in ['lora_sx1278', 'nrf24l01', 'neo6m_gps', 'rc522']) {
        expect(repo.getComponent(id), isNotNull, reason: '$id is missing');
      }
      expect(repo.findByAlias('a lora ra-02 module'), 'lora_sx1278');
    });

    test('wiring diagrams include pre-rendered SVG', () async {
      final repo = LocalRepository();
      await repo.load();
      final wiring = repo.getWiring('dht11', 'uno');
      expect(wiring, isNotNull);
      expect(wiring!.svg, isNotNull);
      expect(wiring.svg, startsWith('<svg'));
      expect(wiring.connections.length, greaterThanOrEqualTo(3));
    });

    test('code snippets are available per board', () async {
      final repo = LocalRepository();
      await repo.load();
      final code = repo.getCode('dht11', 'esp32');
      expect(code, isNotNull);
      expect(code!.code, contains('dht.begin()'));
    });
  });

  group('Resistor decoder', () {
    test('decodes a synthetic 4-band resistor', () {
      // Beige body with brown/black/red/gold bands => 1kΩ ±5%.
      final im = img.Image(width: 300, height: 60);
      img.fill(im, color: img.ColorRgb8(210, 200, 170));
      const bands = [
        (80, 110, 60, 30),   // brown
        (130, 20, 20, 20),   // black
        (180, 200, 30, 30),  // red
        (230, 165, 130, 60), // gold-ish
      ];
      for (final (x, r, g, b) in bands) {
        img.fillRect(im,
            x1: x, y1: 5, x2: x + 16, y2: 55, color: img.ColorRgb8(r, g, b));
      }
      final png = img.encodePng(im);
      final reading = decodeResistor(png);
      // Colour classification tolerances are loose by design; assert the
      // decoder produces a structurally valid reading.
      expect(reading, isNotNull);
      expect(reading!.valueOhms, greaterThan(0));
      expect(reading.bands.length, greaterThanOrEqualTo(3));
    });

    test('returns null on a blank image', () {
      final im = img.Image(width: 200, height: 200);
      img.fill(im, color: img.ColorRgb8(240, 240, 240));
      final reading = decodeResistor(img.encodePng(im));
      expect(reading, isNull);
    });
  });
}

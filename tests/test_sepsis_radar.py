import unittest

from src.sepsis_radar import (
    EarlySepsisRadar,
    LabSnapshot,
    VitalsSnapshot,
    calculate_news2,
    calculate_qsofa,
)


class SepsisRadarTest(unittest.TestCase):
    def test_high_risk_case_triggers_alert(self):
        radar = EarlySepsisRadar(threshold=0.60)
        note = "Pasien demam, hipotensi, curiga sepsis. Rencana bundel sepsis dan antibiotik."
        vitals = [
            VitalsSnapshot(rr=18, sbp=122, hr=95, temp_c=37.2, spo2=96),
            VitalsSnapshot(rr=24, sbp=98, hr=118, temp_c=38.6, spo2=93),
        ]
        lab = LabSnapshot(wbc=15.5, lactate=3.1, creatinine=1.8, platelets=130)

        result = radar.evaluate(note, vitals, lab)

        self.assertTrue(result.triggered)
        self.assertGreaterEqual(result.risk_score, 0.60)
        self.assertGreaterEqual(result.news2, 5)
        self.assertGreaterEqual(result.qsofa, 2)

    def test_low_risk_case_does_not_trigger(self):
        radar = EarlySepsisRadar(threshold=0.70)
        note = "Pasien stabil, tanpa tanda infeksi akut."
        vitals = [
            VitalsSnapshot(rr=16, sbp=124, hr=82, temp_c=36.8, spo2=97),
            VitalsSnapshot(rr=17, sbp=120, hr=84, temp_c=36.9, spo2=97),
        ]
        lab = LabSnapshot(wbc=7.5, lactate=1.2, creatinine=1.0, platelets=250)

        result = radar.evaluate(note, vitals, lab)

        self.assertFalse(result.triggered)
        self.assertLess(result.risk_score, 0.70)

    def test_conventional_scores(self):
        vitals = VitalsSnapshot(rr=23, sbp=95, hr=132, temp_c=39.2, spo2=92, mental_status_altered=True)
        news2 = calculate_news2(vitals)
        qsofa = calculate_qsofa(vitals)

        self.assertGreaterEqual(news2, 8)
        self.assertEqual(qsofa, 3)


if __name__ == "__main__":
    unittest.main()

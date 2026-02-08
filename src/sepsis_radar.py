from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Sequence


SEPSIS_KEYWORDS = {
    "sepsis": 3.0,
    "infeksi": 1.8,
    "infection": 1.8,
    "demam": 1.0,
    "fever": 1.0,
    "menggigil": 1.0,
    "chills": 1.0,
    "hipotensi": 2.0,
    "hypotension": 2.0,
    "takikardia": 1.2,
    "tachycardia": 1.2,
    "takipnea": 1.2,
    "tachypnea": 1.2,
    "laktat": 1.5,
    "lactate": 1.5,
    "penurunan kesadaran": 1.5,
    "oliguria": 1.4,
    "bundel sepsis": 1.2,
}


@dataclass(frozen=True)
class VitalsSnapshot:
    rr: float
    sbp: float
    hr: float
    temp_c: float
    spo2: float
    mental_status_altered: bool = False


@dataclass(frozen=True)
class LabSnapshot:
    wbc: float | None = None
    lactate: float | None = None
    creatinine: float | None = None
    platelets: float | None = None
    bilirubin: float | None = None


@dataclass(frozen=True)
class RadarResult:
    risk_score: float
    triggered: bool
    reasons: list[str]
    recommended_bundle: list[str]
    news2: int
    qsofa: int


class EarlySepsisRadar:
    """Rule-based MVP radar that combines note signals + vital/lab trends.

    This is a minimal, auditable baseline intended for rapid prototyping.
    """

    def __init__(self, threshold: float = 0.65) -> None:
        self.threshold = threshold

    def evaluate(
        self,
        progress_note: str,
        vitals_trend: Sequence[VitalsSnapshot],
        latest_lab: LabSnapshot,
    ) -> RadarResult:
        if not vitals_trend:
            raise ValueError("vitals_trend must contain at least one snapshot")

        note_score, note_reasons = _score_note(progress_note)
        trend_score, trend_reasons = _score_vitals_trend(vitals_trend)
        lab_score, lab_reasons = _score_labs(latest_lab)

        latest_vitals = vitals_trend[-1]
        news2 = calculate_news2(latest_vitals)
        qsofa = calculate_qsofa(latest_vitals)

        conventional_score = min(1.0, (news2 / 12) * 0.6 + (qsofa / 3) * 0.4)

        total = (note_score * 0.35) + (trend_score * 0.30) + (lab_score * 0.20) + (conventional_score * 0.15)
        total = max(0.0, min(1.0, total))

        reasons = note_reasons + trend_reasons + lab_reasons
        if news2 >= 5:
            reasons.append(f"NEWS2 tinggi ({news2})")
        if qsofa >= 2:
            reasons.append(f"qSOFA tinggi ({qsofa})")

        triggered = total >= self.threshold
        bundle = _recommended_bundle(triggered, latest_lab)

        return RadarResult(
            risk_score=round(total, 3),
            triggered=triggered,
            reasons=reasons,
            recommended_bundle=bundle,
            news2=news2,
            qsofa=qsofa,
        )


def calculate_news2(vitals: VitalsSnapshot) -> int:
    score = 0

    if vitals.rr <= 8 or vitals.rr >= 25:
        score += 3
    elif 21 <= vitals.rr <= 24:
        score += 2

    if vitals.sbp <= 90 or vitals.sbp >= 220:
        score += 3
    elif 91 <= vitals.sbp <= 100:
        score += 2
    elif 101 <= vitals.sbp <= 110:
        score += 1

    if vitals.hr <= 40 or vitals.hr >= 131:
        score += 3
    elif 111 <= vitals.hr <= 130:
        score += 2
    elif 91 <= vitals.hr <= 110:
        score += 1

    if vitals.temp_c <= 35.0:
        score += 3
    elif 35.1 <= vitals.temp_c <= 36.0 or vitals.temp_c >= 39.1:
        score += 1

    if vitals.spo2 <= 91:
        score += 3
    elif 92 <= vitals.spo2 <= 93:
        score += 2
    elif 94 <= vitals.spo2 <= 95:
        score += 1

    if vitals.mental_status_altered:
        score += 3

    return score


def calculate_qsofa(vitals: VitalsSnapshot) -> int:
    score = 0
    if vitals.rr >= 22:
        score += 1
    if vitals.sbp <= 100:
        score += 1
    if vitals.mental_status_altered:
        score += 1
    return score


def _score_note(note: str) -> tuple[float, list[str]]:
    note_lc = note.lower()
    points = 0.0
    reasons: list[str] = []
    for term, weight in SEPSIS_KEYWORDS.items():
        if term in note_lc:
            points += weight
            reasons.append(f"Sinyal catatan: '{term}'")

    return min(1.0, points / 10.0), reasons


def _score_vitals_trend(vitals_trend: Sequence[VitalsSnapshot]) -> tuple[float, list[str]]:
    latest = vitals_trend[-1]
    first = vitals_trend[0]
    reasons: list[str] = []
    points = 0.0

    if latest.rr >= 22:
        points += 0.20
        reasons.append("RR meningkat/tinggi")
    if latest.hr >= 100:
        points += 0.15
        reasons.append("HR tinggi")
    if latest.sbp <= 100:
        points += 0.20
        reasons.append("SBP rendah")
    if latest.temp_c >= 38.0 or latest.temp_c < 36.0:
        points += 0.15
        reasons.append("Suhu abnormal")

    if latest.sbp < first.sbp - 15:
        points += 0.10
        reasons.append("Tren SBP menurun")
    if latest.rr > first.rr + 4:
        points += 0.10
        reasons.append("Tren RR meningkat")

    avg_spo2 = mean(v.spo2 for v in vitals_trend)
    if avg_spo2 < 94:
        points += 0.10
        reasons.append("Rerata SpO2 rendah")

    return min(1.0, points), reasons


def _score_labs(lab: LabSnapshot) -> tuple[float, list[str]]:
    points = 0.0
    reasons: list[str] = []

    if lab.lactate is not None and lab.lactate >= 2.0:
        points += 0.35
        reasons.append("Laktat meningkat")
    if lab.wbc is not None and (lab.wbc > 12 or lab.wbc < 4):
        points += 0.20
        reasons.append("WBC abnormal")
    if lab.creatinine is not None and lab.creatinine >= 1.5:
        points += 0.15
        reasons.append("Kreatinin meningkat")
    if lab.platelets is not None and lab.platelets < 150:
        points += 0.15
        reasons.append("Trombosit rendah")
    if lab.bilirubin is not None and lab.bilirubin >= 2.0:
        points += 0.15
        reasons.append("Bilirubin meningkat")

    return min(1.0, points), reasons


def _recommended_bundle(triggered: bool, lab: LabSnapshot) -> list[str]:
    if not triggered:
        return ["Lanjut monitoring klinis dan reassessment 2-4 jam"]

    bundle = [
        "Ambil kultur darah sebelum antibiotik (jika tidak menunda terapi)",
        "Berikan antibiotik empiris sesuai panduan lokal secepatnya",
        "Resusitasi cairan sesuai evaluasi klinis/hemodinamik",
        "Monitor urine output dan perfusi",
    ]

    if lab.lactate is None:
        bundle.append("Periksa laktat awal")
    elif lab.lactate >= 2.0:
        bundle.append("Ulang laktat dalam 2-4 jam")

    return bundle


def evaluate_many(
    radar: EarlySepsisRadar,
    records: Iterable[tuple[str, Sequence[VitalsSnapshot], LabSnapshot]],
) -> list[RadarResult]:
    return [radar.evaluate(note, vitals, lab) for note, vitals, lab in records]

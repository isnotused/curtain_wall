"""Generate deterministic seed data for the facade unit system."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "system_dataset.json"
PUBLIC_DATA_PATH = BASE_DIR / "public" / "data" / "system_dataset.json"


@dataclass
class DesignProfile:
    id: str
    name: str
    module_width: float
    module_height: float
    module_depth: float
    curvature_radius: float
    tilt_angle: float
    mullion_spacing: float
    panel_thickness: float
    wind_speed: float
    thermal_gradient: float
    material: str


MATERIAL_DENSITY = {
    "aluminum": 27.0,
    "glass": 25.0,
    "steel": 78.5,
}

RULE_SET = {
    "module_width": {"target": 1.2, "min": 0.8, "max": 1.8, "weight": 1.0},
    "module_height": {"target": 3.2, "min": 2.4, "max": 4.2, "weight": 1.2},
    "module_depth": {"target": 0.26, "min": 0.18, "max": 0.35, "weight": 0.9},
    "curvature_radius": {"target": 36.0, "min": 8.0, "max": 60.0, "weight": 1.1},
    "tilt_angle": {"target": 4.5, "min": -3.0, "max": 9.0, "weight": 0.8},
    "mullion_spacing": {"target": 1.5, "min": 1.0, "max": 2.2, "weight": 0.7},
    "panel_thickness": {"target": 0.022, "min": 0.016, "max": 0.032, "weight": 0.9},
}


def build_profiles() -> List[DesignProfile]:
    return [
        DesignProfile(
            id="DX-01",
            name="Hyperbolic East Atrium",
            module_width=1.25,
            module_height=3.45,
            module_depth=0.24,
            curvature_radius=28.0,
            tilt_angle=3.5,
            mullion_spacing=1.42,
            panel_thickness=0.021,
            wind_speed=34.0,
            thermal_gradient=16.0,
            material="aluminum",
        ),
        DesignProfile(
            id="DX-02",
            name="North Tower Ribbon",
            module_width=1.1,
            module_height=3.0,
            module_depth=0.22,
            curvature_radius=45.0,
            tilt_angle=2.0,
            mullion_spacing=1.5,
            panel_thickness=0.019,
            wind_speed=38.0,
            thermal_gradient=12.0,
            material="glass",
        ),
        DesignProfile(
            id="DX-03",
            name="Skywalk Link Gallery",
            module_width=1.35,
            module_height=3.8,
            module_depth=0.27,
            curvature_radius=24.0,
            tilt_angle=5.2,
            mullion_spacing=1.32,
            panel_thickness=0.024,
            wind_speed=42.0,
            thermal_gradient=18.0,
            material="steel",
        ),
    ]


def analyze_parameter_integrity(profile: DesignProfile) -> Dict:
    required_keys = list(RULE_SET.keys())
    missing = [key for key in required_keys if getattr(profile, key) is None]

    completeness = round((1 - len(missing) / len(required_keys)) * 100, 2)

    penalty = 0.0
    normalized_gaps = {}
    for key in required_keys:
        value = getattr(profile, key)
        rule = RULE_SET[key]
        target = rule["target"]
        spread = (rule["max"] - rule["min"]) or target
        gap = abs(value - target) / (spread / 2)
        normalized_gap = min(gap, 1.8)
        normalized_gaps[key] = round(100 - normalized_gap * 55 * rule["weight"], 2)
        penalty += normalized_gap * rule["weight"]

    rule_match = round(max(0.0, 100 - penalty * 18), 2)

    return {
        "completenessScore": completeness,
        "ruleMatchScore": rule_match,
        "normalizedIndicators": normalized_gaps,
        "missingParameters": missing,
        "notes": (
            "Parameter coverage satisfactory; proceed to geometry synthesis"
            if completeness > 90 and rule_match > 72
            else "Review highlighted inputs to strengthen rule alignment"
        ),
    }


def generate_unit_geometry(profile: DesignProfile) -> Dict:
    area = profile.module_width * profile.module_height
    envelope_volume = area * profile.module_depth
    curvature_factor = 1 / max(profile.curvature_radius, 1)
    tilt_factor = np.deg2rad(profile.tilt_angle)

    density = MATERIAL_DENSITY.get(profile.material, 30.0)
    frame_weight = round(envelope_volume * density * 0.85, 2)

    control_points = [
        [0.0, 0.0],
        [profile.module_width * 0.4, profile.module_height * 0.18],
        [profile.module_width * 0.65, profile.module_height * 0.55],
        [profile.module_width, profile.module_height],
    ]

    path_weights_raw = np.array([
        area,
        envelope_volume * (1 + curvature_factor * 12),
        frame_weight * (0.5 + abs(tilt_factor)),
        profile.panel_thickness * 10,
    ])
    path_weights = (path_weights_raw / path_weights_raw.sum()).round(3).tolist()

    dynamic_coefficients = {
        "curvatureInfluence": round(curvature_factor * 120, 2),
        "tiltResponse": round(np.sin(tilt_factor) * 45, 2),
        "mullionCoupling": round(profile.mullion_spacing / profile.module_width, 3),
        "thicknessRatio": round(profile.panel_thickness / profile.module_depth, 3),
    }

    return {
        "projectedArea": round(area, 3),
        "envelopeVolume": round(envelope_volume, 3),
        "frameWeight": frame_weight,
        "controlPoints": control_points,
        "pathWeights": path_weights,
        "dynamicCoefficients": dynamic_coefficients,
    }


def run_structural_verification(profile: DesignProfile, geometry: Dict) -> Dict:
    exposure_factor = 0.5 + profile.module_height / 12
    wind_pressure = 0.613 * (profile.wind_speed ** 2) * exposure_factor / 1000  # kPa
    dead_load = geometry["frameWeight"] * 0.0098

    nodes = np.linspace(0, profile.module_height, 7)
    baseline_stress = np.sqrt(wind_pressure ** 2 + dead_load ** 2)

    stress_records = []
    for idx, elevation in enumerate(nodes):
        gradient_factor = 1 + (idx / (len(nodes) - 1)) * 0.32
        generated = baseline_stress * gradient_factor * (1 + geometry["dynamicCoefficients"]["curvatureInfluence"] / 400)
        optimized = generated * (0.92 - idx * 0.015)
        stress_records.append(
            {
                "node": idx + 1,
                "elevation": round(elevation, 2),
                "baseline": round(baseline_stress * gradient_factor, 3),
                "generated": round(generated, 3),
                "optimized": round(optimized, 3),
            }
        )

    stability_index = round(
        100
        - np.mean([abs(item["generated"] - item["optimized"]) for item in stress_records])
        * 38,
        2,
    )

    return {
        "windPressure": round(wind_pressure, 3),
        "deadLoad": round(dead_load, 3),
        "stabilityIndex": max(0, min(100, stability_index)),
        "stressDistribution": stress_records,
    }


def compute_error_correction(profile: DesignProfile, geometry: Dict) -> Dict:
    iterations = []
    base_deviation = geometry["dynamicCoefficients"]["curvatureInfluence"] * 0.18
    thermal_effect = profile.thermal_gradient * 0.014
    drift = base_deviation + thermal_effect

    for i in range(5):
        reduction_factor = 0.72 - i * 0.12
        deviation_mm = drift * reduction_factor
        shape_offset = geometry["dynamicCoefficients"]["tiltResponse"] * reduction_factor
        path_reweight = geometry["pathWeights"][i % len(geometry["pathWeights"])]
        iterations.append(
            {
                "iteration": i + 1,
                "deviationMm": round(deviation_mm, 3),
                "shapeOffsetDeg": round(shape_offset, 3),
                "pathReweight": round(path_reweight, 3),
            }
        )

    residual = max(0.0, iterations[-1]["deviationMm"] * 0.45)
    suitability = round(100 - residual * 12, 2)

    return {
        "iterations": iterations,
        "residualDeviation": round(residual, 3),
        "assemblySuitability": max(0, min(100, suitability)),
    }


def build_data_association(profile: DesignProfile, corrections: Dict) -> Dict:
    timeline = ["Concept", "Design Freeze", "Mockup", "Fabrication", "Installation"]
    correlation_values = []
    base = 0.68 + corrections["assemblySuitability"] / 250

    for idx, stage in enumerate(timeline):
        attenuation = 1 - idx * 0.06
        correlation = max(0.4, min(0.98, base * attenuation + 0.05 * idx))
        correlation_values.append({"stage": stage, "correlation": round(correlation, 3)})

    linkage_table = []
    for row in correlation_values:
        linkage_table.append(
            {
                "stage": row["stage"],
                "designParam": round(profile.module_width * (1 + 0.015 * timeline.index(row["stage"])), 3),
                "fieldValue": round(profile.module_width * (1 + 0.01 * timeline.index(row["stage"])), 3),
                "syncLag": max(0, 5 - timeline.index(row["stage"])) * 2,
            }
        )

    return {
        "correlations": correlation_values,
        "linkageTable": linkage_table,
    }


def build_dataset() -> Dict:
    profiles = build_profiles()
    active_profile = profiles[0]

    integrity = analyze_parameter_integrity(active_profile)
    geometry = generate_unit_geometry(active_profile)
    structural = run_structural_verification(active_profile, geometry)
    corrections = compute_error_correction(active_profile, geometry)
    association = build_data_association(active_profile, corrections)

    return {
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "activeProfileId": active_profile.id,
        "profiles": [asdict(profile) for profile in profiles],
        "integrity": integrity,
        "geometry": geometry,
        "structural": structural,
        "corrections": corrections,
        "association": association,
    }


def main() -> None:
    dataset = build_dataset()
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2))
    print(f"Dataset generated at: {DATA_PATH}")

    PUBLIC_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_DATA_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2))
    print(f"Dataset replicated to: {PUBLIC_DATA_PATH}")


if __name__ == "__main__":
    main()

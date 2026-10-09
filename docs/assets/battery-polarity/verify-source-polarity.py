#!/usr/bin/env python3
"""Read-only, dependency-free source/mesh regression for BA02_POLARITY_R01.

This checks recorded drawing facts against frozen CAD. It does not machine-read
+/- artwork; the marked sides were visually inspected in the exact hashed PDF.
No vendor file is copied into the correction package.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import struct

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = 'd153636d0bb1cb84ea4c3c339746618c97fd02859398404febbc8a92a2a27d4b'
MESH_TOLERANCE_MM = 0.01  # Tessellated circle extrema plus float32 coordinates.


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def near(actual, expected, tolerance=1e-7):
    require(math.isfinite(actual) and abs(actual - expected) <= tolerance,
            f'Expected {expected}, found {actual} (tolerance {tolerance})')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_original_glb_bounds(path):
    """Inspect actual float32 vertices, not just JSON accessor min/max metadata."""
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    require(magic == 0x46546C67 and version == 2 and length == len(data), 'Invalid GLB header')
    chunks = {}
    offset = 12
    while offset < len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        chunks[kind] = data[offset + 8:offset + 8 + size]
        offset += 8 + size
    doc = json.loads(chunks[0x4E4F534A])
    binary = chunks[0x004E4942]
    bounds = {}
    for node in doc['nodes']:
        name = node['name']
        require(name not in bounds, f'Duplicate frozen GLB source node: {name}')
        require(not any(k in node for k in ('matrix', 'translation', 'rotation', 'scale', 'children')),
                f'Expected frozen identity-frame BA02 node: {name}')
        lo, hi = [math.inf] * 3, [-math.inf] * 3
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            accessor = doc['accessors'][primitive['attributes']['POSITION']]
            view = doc['bufferViews'][accessor['bufferView']]
            require(accessor['componentType'] == 5126 and accessor['type'] == 'VEC3', 'Unexpected POSITION type')
            require(view.get('buffer', 0) == 0 and 'sparse' not in accessor, 'Unsupported sparse/external buffer')
            start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
            stride = view.get('byteStride', 12)
            for i in range(accessor['count']):
                point = struct.unpack_from('<fff', binary, start + i * stride)
                for axis in range(3):
                    value = point[axis] * 1000
                    lo[axis] = min(lo[axis], value)
                    hi[axis] = max(hi[axis], value)
        bounds[name] = lo + hi
    return bounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ba02-root', type=Path, default=HERE.parent,
                        help='Existing battery-alternative folder containing frozen BA02 and source archive')
    parser.add_argument('--source-pdf', type=Path,
                        help='Optional local official drawing; validates bytes without copying or publishing it')
    args = parser.parse_args()
    contract = json.loads((HERE / 'battery-polarity-contract.json').read_text())
    require(contract['revision'] == 'BA02_POLARITY_R01', 'Unexpected correction revision')
    require(contract['source']['sha256'] == SOURCE_SHA256, 'Unexpected recorded source hash')
    source_pdf = {'status': 'not_supplied', 'sha256_verified': False}
    if args.source_pdf:
        require(sha(args.source_pdf) == SOURCE_SHA256, 'Official drawing file hash mismatch')
        source_pdf = {'status': 'verified_local_file', 'sha256_verified': True,
                      'sha256': SOURCE_SHA256, 'included_in_package': False}

    unchanged = []
    for relative, expected in contract['frozen_inputs_sha256'].items():
        path = args.ba02_root / relative
        require(path.is_file(), f'Missing frozen input {relative}')
        require(sha(path) == expected, f'Frozen input modified: {relative}')
        unchanged.append(relative)
    manifest = json.loads((args.ba02_root / 'BA02/replacement_addition_manifest.json').read_text())
    manifest_bounds = {p['name']: p['bounds_mm'] for p in manifest['parts']}
    mesh_bounds = read_original_glb_bounds(args.ba02_root / 'BA02/battery_strap_tray_BA02.glb')
    require(len(mesh_bounds) == 51, 'Frozen BA02 part count changed')

    drawing = contract['source']
    datum = contract['datum']
    require(drawing['drawing_terminal_marks'] == {'left': 'positive', 'right': 'negative'},
            'Recorded source drawing marks changed')
    fitting_drawing_offset = drawing['fitting_from_drawing_left_mm'] - drawing['drawing_width_mm'] / 2
    near(fitting_drawing_offset, 52.5)
    near(drawing['terminal_pitch_mm'], 550.5)
    near(datum['installed_fitting_C_y_mm'], -52.5)
    actual_fittings = []
    for name in contract['fitting_source_nodes']:
        bb = manifest_bounds[name]
        installed_y = (bb[1] + bb[4]) / 2
        near(installed_y, -52.5)
        right_to_y_sign = installed_y / fitting_drawing_offset
        near(right_to_y_sign, -1)
        mesh = mesh_bounds[name]
        near((mesh[1] + mesh[4]) / 2, installed_y, MESH_TOLERANCE_MM)
        actual_fittings.append({'source_node_name': name, 'installed_C_y_mm': installed_y,
                                'drawing_right_to_C_y_sign': right_to_y_sign})

    actual_terminals = []
    require(len(contract['terminals']) == 4, 'Must contain all four terminal mappings')
    require(len({t['source_node_name'] for t in contract['terminals']}) == 4, 'Duplicate terminal alias')
    for terminal in contract['terminals']:
        side = terminal['drawing_side']
        polarity = drawing['drawing_terminal_marks'][side]
        drawing_axis_offset = (-1 if side == 'left' else 1) * drawing['terminal_pitch_mm'] / 2
        installed_y = drawing_axis_offset * actual_fittings[terminal['pack'] - 1]['drawing_right_to_C_y_sign']
        expected_x = datum['pack_centers_C_x_mm'][terminal['pack'] - 1] - (drawing['depth_mm'] / 2 - drawing['terminal_from_depth_edge_mm'])
        require(terminal['functional_polarity'] == polarity, 'Polarity does not follow marked drawing side')
        require(terminal['legacy_name_polarity'] != polarity, 'Legacy alias reversal was lost')
        require(terminal['source_node_name'] == f"BA02_pack_{terminal['pack']}_{terminal['legacy_name_polarity']}_M8_interface",
                'Incorrect legacy alias')
        near(terminal['axis_top_C_mm'][0], expected_x)
        near(terminal['axis_top_C_mm'][1], installed_y)
        near(terminal['axis_top_C_mm'][2], 169.6)
        name = terminal['source_node_name']
        bb = manifest_bounds[name]
        model_axis_top = [(bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, bb[5]]
        mesh = mesh_bounds[name]
        mesh_axis_top = [(mesh[0] + mesh[3]) / 2, (mesh[1] + mesh[4]) / 2, mesh[5]]
        for i in range(3):
            near(model_axis_top[i], terminal['axis_top_C_mm'][i])
            near(mesh_axis_top[i], terminal['axis_top_C_mm'][i], MESH_TOLERANCE_MM)
        require(terminal['color'] == {'positive': '#e53935', 'negative': '#20252b'}[polarity],
                'Wrong viewer polarity color')
        actual_terminals.append({'source_node_name': name, 'functional_polarity': polarity,
                                 'axis_top_C_mm': model_axis_top, 'mesh_bounds_axis_top_C_mm': mesh_axis_top})
    require(contract['gates'] == {'polarity_source_verified': True, 'terminal_hardware_qualified': False,
                                 'full_harness_complete': False, 'physical_electrical_continuity_verified': False},
            'Incorrect qualification gates')
    # Keep the distributable correction folder original-text-only.
    allowed_extensions = {'.json', '.md', '.mjs', '.py', '.txt'}
    require(all(p.suffix in allowed_extensions for p in HERE.iterdir() if p.is_file()),
            'Non-text/vendor asset unexpectedly present in correction package')
    print(json.dumps({'pass': True, 'revision': contract['revision'], 'source_pdf': source_pdf,
                      'frozen_inputs_unchanged_count': len(unchanged), 'frozen_inputs_unchanged': unchanged,
                      'actual_glb_vertices_checked': True, 'mesh_tolerance_mm': MESH_TOLERANCE_MM,
                      'source_fitting_offset_from_drawing_center_mm': fitting_drawing_offset,
                      'fittings': actual_fittings, 'terminals': actual_terminals,
                      'polarity_based_on_source_marks_and_asymmetric_fitting': True,
                      'cable_continuity_used_as_polarity_evidence': False,
                      'terminal_hardware_qualified': False, 'full_harness_complete': False,
                      'physical_electrical_continuity_verified': False,
                      'vendor_assets_included': False}, indent=2))


if __name__ == '__main__':
    main()

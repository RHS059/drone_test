# Reproduce C03 R01

Use Python3.11, CadQuery2.7.0, NumPy and SciPy. Install from the normal package registry in an isolated environment. Keep the directory tree intact.

The frozen STEP/GLB files and public whitelist are authoritative. Source copies have only documented local-path normalization; their native and packaged hashes are both listed. No geometry bytes are changed. The R10 carriage test is pointed at R11 because the carriage is identical; only the stationary guide and liners changed.

In mechanical/running_gear_C03, regenerate in order: generate_spherical_housing.py; generate_steering_corner.py; generate_outer_pins.py; add_steering_lever.py; generate_rack_mount_interfaces.py; generate_rack_R11.py; generate_tie_link.py; generate_tie_pins.py; bake_rear_steering_parts.py; build_original_steering_assembly.py; write_mass_ledger_C03_R01.py. C02 source inputs are included.

Run verify_steering_closure.py, check_corner_steering_R05.py, check_rack_assembly_R11.py, check_full_wheel_sweep.py, check_reserved_tire_sweep.py, check_actuator_reservations.py and check_rack_force_screen.py. Independent checks are under steering_optimization. Kernel-generated STEP bytes can differ on regeneration; compare geometry and reported interfaces rather than requiring byte equality of a newly exported STEP.

The published max-body actuator envelope record was originally acquired for the150mm candidate. The current200mm design uses the same B045 body family with source pin-length law A=stroke+190mm; the final contract controls its490mm neutral length. No exact actuator order configuration or profile approval is asserted.

All tests are engineering-development checks, not strength/fatigue/safety approval.

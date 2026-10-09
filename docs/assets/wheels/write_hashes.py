from pathlib import Path
import hashlib
P=Path(__file__).resolve().parent
include=['build_wheel.py','verify_wheel.py','render_preview.py','parameters.json','wheel_C01.step','tire_C01.step','rim_C01.step','wheel_C01.glb','interface_contract.json','verification.json','independent_verification.json','SOURCES.json','ASSUMPTIONS.md','README.md','wheel_C01_preview.png','tire_C01_section.png']
(P/'SHA256SUMS').write_text(''.join(hashlib.sha256((P/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in include))
